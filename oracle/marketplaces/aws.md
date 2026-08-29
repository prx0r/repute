# AWS Marketplace — Source Reference

**URL:** https://aws.amazon.com/marketplace
**API Base:** https://catalog.marketplace.aws-api.com
**Status:** LIVE
**Revenue Share:** 100% to seller (AWS takes no cut for SaaS)
**Agent-friendly:** Yes (Catalog API, 10/10 enterprise)

## Key Endpoints

### Catalog
```
POST /Catalog/StartChangeSet           — Create change set
POST /Catalog/DescribeChangeSet        — Describe change set
POST /Catalog/ExecuteChangeSet         — Execute change set
GET  /Catalog/ListResources            — List resources
GET  /Catalog/DescribeResource         — Describe resource
```

### Entitlements
```
POST /Entitlements/ListEntitlements    — List entitlements
POST /Entitlements/ResolveEntitlement  — Resolve entitlement
```

### Metering
```
POST /Metering/MeterUsage              — Report usage
```

## Authentication
- AWS IAM (SigV4)

## Product Types Supported
- SaaS
- Containers (ECS/EKS)
- AMI Software
- Machine Learning Models
- Data Products
- Professional Services
- AI Agent Products

## Data Fields Available

| Field | Available | Notes |
|-------|-----------|-------|
| resource.id | ✅ | Product ID |
| resource.name | ✅ | Product name |
| resource.type | ✅ | SaaS, AMI, Container, etc. |
| resource.price | ✅ | Pricing model |
| resource.status | ✅ | Published/Draft |
| entitlement.id | ✅ | Customer entitlement |
| metering.dimension | ✅ | Usage dimension |
