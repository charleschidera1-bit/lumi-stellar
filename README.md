Lumi
Stellar User Onboarding, Fee Sponsorship & Web3 Actions Infrastructure
Lumi is an open-source developer infrastructure project designed to help Stellar applications onboard users, sponsor eligible transaction fees, and automate common Web3 actions.
Problem
Stellar projects often need to build similar infrastructure for:
User onboarding
Transaction sponsorship
Rewards
Referrals
Payments
Blockchain automation
Lumi provides reusable infrastructure for these use cases.
Core Features
Lumi Onboard
Simplifies the process of getting new users from wallet connection to their first Stellar transaction.
Lumi Sponsor
Allows participating applications to sponsor eligible Stellar transaction fees for their users.
Lumi Actions
Provides a simple event-based system for triggering blockchain actions such as rewards, payments, and referrals.
Architecture
Stellar Project
       |
       v
   Lumi SDK/API
       |
       +---- Onboarding
       |
       +---- Fee Sponsorship
       |
       +---- Web3 Actions
       |
       v
    Stellar Network
Current Status
Lumi is currently an MVP under development.
The initial version focuses on Stellar Testnet and fee-sponsored transactions.
Roadmap
Project repository
Initial API
Testnet sponsorship demo
Onboarding SDK
Web3 Actions engine
Developer dashboard
Security review
Mainnet readiness
Stellar ecosystem integrations
Security
Lumi will never request or store users' private keys.
The MVP is intended for Testnet development and should not be considered production-ready financial infrastructure.
Contributing
Contributions, issues, feature requests, and developer feedback are welcome.
License
MIT