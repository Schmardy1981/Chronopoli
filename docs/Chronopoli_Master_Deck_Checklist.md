# Abgleich: Master-Papiere (März 2026) ↔ unsere Decks

Master-Papiere: **01 Investor Deck** (16 Folien), **02 Pitch Narrative**, **04 One Pager**. Das Origen-Valley-White-Paper ist **nicht** mehr Grundlage.
Legende: ✅ vorhanden · ⚠️ anders benannt/teilweise · ❌ fehlt · 🔒 Widerspruch, Entscheidung nötig

## A. Was im Pitch-Deck (28 Folien) fehlt oder anders heißt
| # | Master-Papier | Unser Pitch-Deck | Status | Maßnahme |
|---|---|---|---|---|
| A1 | Tagline „AI-Native Knowledge Infrastructure · Community Intelligence Engine · Verified Credentials“ | nur „Global Knowledge City“ | ❌ | Auf dem Cover ergänzen |
| A2 | Problem: Fragmentation · Speed Mismatch (18/6 Monate vs. 48 h) · Fake Credentials · No Neutral Convener | 4 Probleme, ähnlich, andere Titel | ⚠️ | Titel an die Master-Begriffe angleichen, Speed-Mismatch-Fakt aufnehmen |
| A3 | **Octopus Model**: Chronopoli = Kopf, jede Firma/Institution = Tentakel | fehlt | ❌ | Neue Folie nach „The city“ |
| A4 | **Drei Säulen**: Symposia · Company Academies · Open Knowledge (AI Tutor + Digital Twins + Marketplace) | Features vorhanden, aber nicht so gruppiert | ⚠️ | Übersichtsfolie „Three pillars, one platform“ und Säulen-Label auf jeder Feature-Folie |
| A5 | Pipeline „5 Outputs in 3 Stunden, ein Mensch, 10 Min., APPROVE“; 5. Output = AI-Tutor-Knowledge-Update | 6 Outputs, Freigabe durch Moderator | ⚠️ | Master-Formulierung übernehmen, AI-Tutor-Update als Output ergänzen |
| A6 | Markt: TAM $45B · SAM $8.5B · SOM $9.6M (Y3) + 5 Teilmärkte mit CAGR | fehlt (bewusst keine Marktzahlen) | ❌ | Folie „Market opportunity“, Quelle: „Chronopoli Master Document estimates“ |
| A7 | Business Model: Academies $25K–150K/Jahr · Corporate Team Subs $1,500/Seat/Jahr · Individual Subs $490–1,490/Jahr · Marketplace 70/30 · $15/Zertifikat · Summit ab Jahr 2; Y1 $1.72M, Y3 $9.59M | Layer-Preise pro Kurs, $125/Seat/Monat (= $1,500/Jahr ✅), 70/30 ✅ | ⚠️ | Master-Preismodell als Business-Model-Folie; unsere Kurs-Layer als Plattform-Mechanik darunter |
| A8 | Financials: 67.5 % EBITDA Y1, Cash Y5 $44.9M, AWS $4,572/Jahr, Claude $3,300, ElevenLabs+HeyGen $612 | fehlt | ❌ | Folie „Financial highlights“ als Projektion gekennzeichnet |
| A9 | Traction: DBCC bestätigter Anker (500+ Firmen) · BUiD-MOU in Arbeit (Maria Papadaki, 30 CPD-Credits) · Ripple „pitching“ · Chainalysis „engaging“ · 15 GSD-Phasen / 90 Requirements | nur Roadmap-Ziele „nicht unterzeichnet“ | ⚠️ | Traction-Folie mit genau diesen Status-Angaben |
| A10 | Wettbewerb: Tabelle vs. Coursera/LinkedIn, ACAMS/ICA, Vendor Academies | fehlt | ❌ | Folie „We are not a better Coursera“ |
| A11 | Vier Moats: Knowledge · Partner Lock-in · Network Effects · Cost Structure | fehlt | ❌ | Folie nach Wettbewerb |
| A12 | Team: Chris (Co-Founder & COO), CTO (TBC), Advisors Maria Papadaki (BUiD), DBCC Leadership | fehlt | ❌ | Team-Folie |
| A13 | GTM: 90-Tage-Sprint, Phasen NOW→M3 / M3→M6 / M6→M12 / M12→M24 | 6-Sprint-Plan (Technik) | ⚠️ | GTM-Folie ergänzen, 6-Sprint-Plan als technischer Unterbau |
| A14 | Ask: $2M Seed, $8M pre-money, SAFE/Equity, 18 Monate Runway, Mittelverwendung | Ask „Founding Knowledge Partner“ | ❌ | Investor-Ask ergänzen (Partner-Ask bleibt als zweite Option) |
| A15 | Closing-Statement „Chronopoli is not a better Coursera …“ | fehlt | ❌ | Als Schlussfolie |
| A16 | 7 Knowledge Districts (Anhang) | vorhanden | ✅ | — |

## B. Widersprüche zwischen Master-Papieren und geprüftem Code-Stand (🔒)
| # | Master-Aussage | Befund aus Review / Code | Vorgeschlagener Default |
|---|---|---|---|
| B1 | „Platform is LIVE … Deploy in 24 hours“, „Profitable from Month 5“ | Noch nicht deployed; 37 Review-Befunde, 6 kritisch (u. a. Django-Apps nicht installierbar) | „Code-complete, Terraform-ready; go-live after a six-sprint hardening plan“ – kein „live“ |
| B2 | Pipeline „Zero staff“, „Auto-publish“ auch TikTok | Pipeline erzeugt LinkedIn/Instagram/Report/Paper, **Freigabe durch einen Menschen**; kein TikTok im Code | „One human approves in ~10 min“; TikTok als Roadmap |
| B3 | AWS $374/Monat | CLAUDE.md: ~$430/Monat (Phase 1) | Master-Zahl $374 verwenden (ist die Master-Quelle) |
| B4 | Individual-Abos $490–1,490/Jahr | Code verkauft Kurse einzeln nach Layer ($0–8,000) | Beides zeigen: Abo = kommerzielles Modell, Layer-Preise = Einzelkauf |
| B5 | Markt- und Finanzzahlen ohne Quellen | — | Als „Master Document estimates / projections“ beschriften |
| B6 | „9,500+ lines · 148 files“ | aktueller Stand größer (90 Python-Dateien + Terraform + Lambdas …) | Weglassen oder neu zählen |

## C. Sales-Deck
Die Punkte A3, A4, A5, A7 (Preise für Academies $25K–150K/Jahr, Seats $1,500/Jahr), A9, A10, A11 und A15 fließen auch ins Sales-Deck. **Nicht** ins Sales-Deck: A6 (Markt), A8 (Finanzen), A14 (Investor-Ask).
