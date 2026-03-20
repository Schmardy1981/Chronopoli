# ============================================================
# Chronopoli – Step Functions State Machine (Symposia Pipeline)
# ============================================================

# IAM Role for Step Functions
resource "aws_iam_role" "symposia_sfn" {
  name = "${var.project_name}-symposia-sfn-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "states.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(var.tags, {
    Component = "Symposia"
  })
}

# Allow Step Functions to invoke all Symposia Lambda functions
resource "aws_iam_role_policy" "symposia_sfn_lambda" {
  name = "symposia-sfn-lambda-invoke"
  role = aws_iam_role.symposia_sfn.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction"
        ]
        Resource = [
          aws_lambda_function.symposia_transcribe.arn,
          aws_lambda_function.symposia_check_transcription.arn,
          aws_lambda_function.symposia_analyze.arn,
          aws_lambda_function.symposia_opinion_paper.arn,
          aws_lambda_function.symposia_linkedin.arn,
          aws_lambda_function.symposia_instagram.arn,
          aws_lambda_function.symposia_partner_report.arn,
          aws_lambda_function.symposia_notify.arn,
        ]
      }
    ]
  })
}

# State Machine
resource "aws_sfn_state_machine" "symposia_pipeline" {
  name     = "${var.project_name}-symposia-pipeline-${var.environment}"
  role_arn = aws_iam_role.symposia_sfn.arn

  definition = jsonencode({
    Comment = "Chronopoli Symposia Pipeline – Processes round table recordings into multi-format outputs"
    StartAt = "StartTranscription"

    States = {

      # Step 1: Submit AWS Transcribe job
      StartTranscription = {
        Type     = "Task"
        Resource = "arn:aws:states:::lambda:invoke"
        Parameters = {
          FunctionName = aws_lambda_function.symposia_transcribe.arn
          Payload = {
            "recording_s3_uri.$" = "$.recording_s3_uri"
            "round_table_id.$"   = "$.round_table_id"
          }
        }
        ResultPath = "$.transcription"
        ResultSelector = {
          "job_name.$"       = "$.Payload.job_name"
          "round_table_id.$" = "$.Payload.round_table_id"
        }
        Next = "WaitForTranscription"
      }

      # Step 2: Wait 30 seconds before checking
      WaitForTranscription = {
        Type    = "Wait"
        Seconds = 30
        Next    = "CheckTranscription"
      }

      # Step 3: Check transcription status
      CheckTranscription = {
        Type     = "Task"
        Resource = "arn:aws:states:::lambda:invoke"
        Parameters = {
          FunctionName = aws_lambda_function.symposia_check_transcription.arn
          Payload = {
            "job_name.$"       = "$.transcription.job_name"
            "round_table_id.$" = "$.transcription.round_table_id"
          }
        }
        ResultPath = "$.transcription_result"
        ResultSelector = {
          "status.$"            = "$.Payload.status"
          "transcript_text.$"   = "$.Payload.transcript_text"
          "transcript_s3_key.$" = "$.Payload.transcript_s3_key"
          "job_name.$"          = "$.Payload.job_name"
          "round_table_id.$"    = "$.Payload.round_table_id"
        }
        Next = "IsTranscriptionComplete"
      }

      # Step 3b: Choice – loop or proceed
      IsTranscriptionComplete = {
        Type = "Choice"
        Choices = [
          {
            Variable     = "$.transcription_result.status"
            StringEquals = "COMPLETED"
            Next         = "AnalyzeWithClaude"
          },
          {
            Variable     = "$.transcription_result.status"
            StringEquals = "FAILED"
            Next         = "TranscriptionFailed"
          }
        ]
        Default = "WaitForTranscription"
      }

      # Error state for failed transcription
      TranscriptionFailed = {
        Type  = "Fail"
        Error = "TranscriptionFailed"
        Cause = "AWS Transcribe job failed"
      }

      # Step 4: Analyze transcript with Bedrock Claude
      AnalyzeWithClaude = {
        Type     = "Task"
        Resource = "arn:aws:states:::lambda:invoke"
        Parameters = {
          FunctionName = aws_lambda_function.symposia_analyze.arn
          Payload = {
            "transcript_text.$" = "$.transcription_result.transcript_text"
            "round_table_id.$"  = "$.transcription_result.round_table_id"
          }
        }
        ResultPath = "$.analysis_result"
        ResultSelector = {
          "analysis.$"       = "$.Payload.analysis"
          "round_table_id.$" = "$.Payload.round_table_id"
        }
        Next = "GenerateOutputsParallel"
      }

      # Step 5: Generate all outputs in parallel
      GenerateOutputsParallel = {
        Type = "Parallel"
        Branches = [
          {
            StartAt = "GenerateOpinionPaper"
            States = {
              GenerateOpinionPaper = {
                Type     = "Task"
                Resource = "arn:aws:states:::lambda:invoke"
                Parameters = {
                  FunctionName = aws_lambda_function.symposia_opinion_paper.arn
                  Payload = {
                    "analysis.$"       = "$.analysis_result.analysis"
                    "round_table_id.$" = "$.analysis_result.round_table_id"
                    "district_codes.$" = "$.district_codes"
                  }
                }
                ResultSelector = {
                  "opinion_paper_key.$" = "$.Payload.s3_key"
                }
                End = true
              }
            }
          },
          {
            StartAt = "GenerateLinkedIn"
            States = {
              GenerateLinkedIn = {
                Type     = "Task"
                Resource = "arn:aws:states:::lambda:invoke"
                Parameters = {
                  FunctionName = aws_lambda_function.symposia_linkedin.arn
                  Payload = {
                    "analysis.$"       = "$.analysis_result.analysis"
                    "round_table_id.$" = "$.analysis_result.round_table_id"
                  }
                }
                ResultSelector = {
                  "linkedin_key.$" = "$.Payload.s3_key"
                }
                End = true
              }
            }
          },
          {
            StartAt = "GenerateInstagram"
            States = {
              GenerateInstagram = {
                Type     = "Task"
                Resource = "arn:aws:states:::lambda:invoke"
                Parameters = {
                  FunctionName = aws_lambda_function.symposia_instagram.arn
                  Payload = {
                    "analysis.$"       = "$.analysis_result.analysis"
                    "round_table_id.$" = "$.analysis_result.round_table_id"
                  }
                }
                ResultSelector = {
                  "instagram_key.$" = "$.Payload.s3_key"
                }
                End = true
              }
            }
          },
          {
            StartAt = "GeneratePartnerReport"
            States = {
              GeneratePartnerReport = {
                Type     = "Task"
                Resource = "arn:aws:states:::lambda:invoke"
                Parameters = {
                  FunctionName = aws_lambda_function.symposia_partner_report.arn
                  Payload = {
                    "analysis.$"       = "$.analysis_result.analysis"
                    "round_table_id.$" = "$.analysis_result.round_table_id"
                  }
                }
                ResultSelector = {
                  "partner_reports_key.$" = "$.Payload.s3_key"
                  "partners_count.$"      = "$.Payload.partners_count"
                }
                End = true
              }
            }
          }
        ]
        ResultPath = "$.parallel_outputs"
        Next       = "NotifyForApproval"
      }

      # Step 6: Notify staff for approval
      NotifyForApproval = {
        Type     = "Task"
        Resource = "arn:aws:states:::lambda:invoke"
        Parameters = {
          FunctionName = aws_lambda_function.symposia_notify.arn
          Payload = {
            "round_table_id.$"     = "$.analysis_result.round_table_id"
            "opinion_paper_key.$"  = "$.parallel_outputs[0].opinion_paper_key"
            "linkedin_key.$"       = "$.parallel_outputs[1].linkedin_key"
            "instagram_key.$"      = "$.parallel_outputs[2].instagram_key"
            "partner_reports_key.$" = "$.parallel_outputs[3].partner_reports_key"
            "analysis_key"         = "analysis.json"
          }
        }
        ResultPath = "$.notification"
        Next       = "Done"
      }

      # Step 7: Success
      Done = {
        Type = "Succeed"
      }
    }
  })

  tags = merge(var.tags, {
    Component = "Symposia"
  })
}
