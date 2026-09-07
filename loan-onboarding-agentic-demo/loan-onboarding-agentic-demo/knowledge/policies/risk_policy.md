# Credit Risk Assessment Policy
Version 1.8 | Effective Date: January 1, 2025

## 1. Risk Scoring Model
Risk Score = f(Credit Score, DTI Ratio, LTV Ratio, Business Age, Industry Risk)

### Credit Score Component (40% weight)
- 780+: 0 points (lowest risk)
- 720–779: 15 points
- 680–719: 30 points
- 650–679: 50 points
- Below 650: INELIGIBLE

### Debt-to-Income (DTI) Ratio (30% weight)
- Below 30%: 5 points
- 30%–44%: 20 points
- 45%–54%: 40 points
- 55%+: INELIGIBLE

### Loan-to-Value (LTV) Ratio (20% weight)
- Below 60%: 5 points
- 60%–79%: 15 points
- 80%–84%: 30 points
- 85%+: INELIGIBLE

### Business Age (10% weight)
- 10+ years: 0 points
- 5–9 years: 5 points
- 3–4 years: 10 points
- Below 3 years: INELIGIBLE

## 2. Risk Categories and Actions
| Score Range | Category   | Recommendation            | Timeline  |
|-------------|------------|---------------------------|-----------|
| 0–29        | LOW        | APPROVE                   | Standard  |
| 30–54       | MEDIUM     | CONDITIONAL_APPROVE       | +2 days   |
| 55–74       | HIGH       | MANUAL_REVIEW             | +5 days   |
| 75–100      | VERY_HIGH  | REJECT                    | Immediate |

## 3. Industry Risk Multipliers
- Transportation & Logistics: 1.1x (moderate risk)
- Manufacturing: 1.0x (standard)
- Real Estate: 1.2x (elevated)
- Retail: 1.15x
- Technology: 0.9x (lower risk)
- Healthcare: 0.85x (lower risk)

## 4. Conditional Approval Requirements (MEDIUM Risk)
- Additional collateral (minimum 10% above standard)
- Personal guarantees from directors
- Quarterly financial reporting
- Restrictive covenants on dividend payments
- Mandatory insurance coverage

## 5. Manual Review Triggers (HIGH Risk)
- Loan amount > $5M
- DTI between 45%–54%
- New business (3–4 years operation)
- Adverse credit events in last 2 years
- Request for waiver on any standard requirement
- Complex ownership structure

## 6. Portfolio Concentration Limits
- Single borrower: Max 10% of portfolio
- Single industry: Max 25% of portfolio
- Geographic concentration: Max 30% of portfolio
