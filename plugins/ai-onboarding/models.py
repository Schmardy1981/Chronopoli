"""
Chronopoli AI Onboarding Plugin
Replaces Engagely AI with a custom OpenEdX-native onboarding flow.

Flow:
1. New user registers on OpenEdX
2. Redirect to /chronopoli/onboarding/
3. AI questionnaire (5 questions) identifies user type + interests
4. Recommends districts, learning layer, and first courses
5. Auto-enrolls user in recommended free/entry courses
6. Sends personalized welcome email
"""

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


# ============================================================
# MODELS
# ============================================================

class OnboardingProfile(models.Model):
    """
    Stores the AI onboarding results for each user.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='chronopoli_profile'
    )
    
    # Completed onboarding?
    onboarding_completed = models.BooleanField(default=False)
    onboarding_completed_at = models.DateTimeField(null=True, blank=True)
    
    # User type (from question 1)
    USER_TYPE_CHOICES = [
        ('regulator', 'Regulator / Government'),
        ('law_enforcement', 'Law Enforcement / FIU'),
        ('bank', 'Bank / Financial Institution'),
        ('exchange', 'Crypto Exchange'),
        ('enterprise', 'Enterprise Leader'),
        ('founder', 'Founder / Startup'),
        ('student', 'Student / Professional'),
        ('consultant', 'Consultant / Advisor'),
        ('other', 'Other'),
    ]
    user_type = models.CharField(
        max_length=50,
        choices=USER_TYPE_CHOICES,
        blank=True
    )
    
    # Primary interest district
    primary_district = models.CharField(max_length=20, blank=True)
    
    # Secondary districts (JSON list)
    secondary_districts = models.JSONField(default=list)
    
    # Recommended learning layer
    LAYER_CHOICES = [
        ('entry', 'L1 – Entry'),
        ('professional', 'L2 – Professional'),
        ('institutional', 'L3 – Institutional'),
        ('influence', 'L4 – Influence'),
    ]
    recommended_layer = models.CharField(
        max_length=20,
        choices=LAYER_CHOICES,
        default='entry'
    )
    
    # Raw questionnaire answers (JSON)
    questionnaire_answers = models.JSONField(default=dict)
    
    # Recommended courses (list of course keys)
    recommended_courses = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Chronopoli Onboarding Profile"
        verbose_name_plural = "Chronopoli Onboarding Profiles"

    def __str__(self):
        return f"{self.user.username} – {self.user_type} ({self.primary_district})"


# ============================================================
# ONBOARDING LOGIC
# ============================================================

DISTRICT_MAPPING = {
    # user_type → primary district recommendation
    'regulator': 'CHRON-GOV',
    'law_enforcement': 'CHRON-INV',
    'bank': 'CHRON-COMP',
    'exchange': 'CHRON-DA',
    'enterprise': 'CHRON-AI',
    'founder': 'CHRON-DA',
    'student': 'CHRON-DA',
    'consultant': 'CHRON-RISK',
    'other': 'CHRON-DA',
}

LAYER_MAPPING = {
    # user_type → recommended learning layer
    'regulator': 'institutional',
    'law_enforcement': 'professional',
    'bank': 'professional',
    'exchange': 'professional',
    'enterprise': 'institutional',
    'founder': 'professional',
    'student': 'entry',
    'consultant': 'professional',
    'other': 'entry',
}

# The 5 onboarding questions
ONBOARDING_QUESTIONS = [
    {
        "id": "q1_role",
        "question": "Which best describes your role?",
        "type": "single_choice",
        "options": [
            {"value": "regulator", "label": "Regulator / Government Official"},
            {"value": "law_enforcement", "label": "Law Enforcement / Financial Intelligence"},
            {"value": "bank", "label": "Bank / Financial Institution"},
            {"value": "exchange", "label": "Crypto Exchange / Digital Asset Business"},
            {"value": "enterprise", "label": "Enterprise Leader / C-Suite"},
            {"value": "founder", "label": "Founder / Startup"},
            {"value": "student", "label": "Student / Early-Career Professional"},
            {"value": "consultant", "label": "Consultant / Advisor"},
        ]
    },
    {
        "id": "q2_focus",
        "question": "What is your primary area of interest?",
        "type": "single_choice",
        "options": [
            {"value": "CHRON-AI", "label": "Artificial Intelligence & Automation"},
            {"value": "CHRON-DA", "label": "Blockchain & Digital Assets"},
            {"value": "CHRON-GOV", "label": "Governance & Regulation"},
            {"value": "CHRON-COMP", "label": "Compliance & AML"},
            {"value": "CHRON-INV", "label": "Financial Crime Investigation"},
            {"value": "CHRON-RISK", "label": "Risk Management & Cybersecurity"},
        ]
    },
    {
        "id": "q3_experience",
        "question": "How would you describe your experience in this field?",
        "type": "single_choice",
        "options": [
            {"value": "beginner", "label": "Just getting started"},
            {"value": "intermediate", "label": "Some experience, looking to deepen knowledge"},
            {"value": "advanced", "label": "Experienced professional"},
            {"value": "expert", "label": "Senior expert / leadership level"},
        ]
    },
    {
        "id": "q4_goal",
        "question": "What is your primary goal on Chronopoli?",
        "type": "single_choice",
        "options": [
            {"value": "awareness", "label": "General awareness of the market"},
            {"value": "skills", "label": "Build practical skills"},
            {"value": "certification", "label": "Earn a professional certificate"},
            {"value": "policy", "label": "Engage with policy and governance dialogue"},
            {"value": "network", "label": "Connect with industry experts"},
        ]
    },
    {
        "id": "q5_urgency",
        "question": "How urgent is your learning need?",
        "type": "single_choice",
        "options": [
            {"value": "immediate", "label": "I need this knowledge now"},
            {"value": "weeks", "label": "Within the next few weeks"},
            {"value": "months", "label": "Over the next few months"},
            {"value": "exploring", "label": "Just exploring for now"},
        ]
    }
]


def calculate_recommendations(answers: dict) -> dict:
    """
    Given questionnaire answers, return district + layer + course recommendations.
    """
    user_type = answers.get('q1_role', 'other')
    focus_district = answers.get('q2_focus', DISTRICT_MAPPING.get(user_type, 'CHRON-DA'))
    experience = answers.get('q3_experience', 'beginner')
    
    # Primary district: use explicit choice (q2) or map from role (q1)
    primary_district = focus_district
    
    # Secondary districts: always include 2 complementary districts
    secondary_map = {
        'CHRON-AI':   ['CHRON-RISK', 'CHRON-COMP'],
        'CHRON-DA':   ['CHRON-COMP', 'CHRON-GOV'],
        'CHRON-GOV':  ['CHRON-DA', 'CHRON-COMP'],
        'CHRON-COMP': ['CHRON-INV', 'CHRON-DA'],
        'CHRON-INV':  ['CHRON-COMP', 'CHRON-DA'],
        'CHRON-RISK': ['CHRON-AI', 'CHRON-COMP'],
    }
    secondary_districts = secondary_map.get(primary_district, ['CHRON-DA', 'CHRON-COMP'])
    
    # Learning layer
    if experience in ['expert', 'advanced']:
        layer = LAYER_MAPPING.get(user_type, 'professional')
        if layer == 'entry':
            layer = 'professional'
    else:
        layer = LAYER_MAPPING.get(user_type, 'entry')
        if experience == 'beginner':
            layer = 'entry'
    
    return {
        'primary_district': primary_district,
        'secondary_districts': secondary_districts,
        'recommended_layer': layer,
        'user_type': user_type,
    }
