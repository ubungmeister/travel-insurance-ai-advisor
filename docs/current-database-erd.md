# Implemented Database ERD

This diagram describes the database implemented by the Python SQLAlchemy models and Alembic migrations. A policy points to one exact plan variant and one exact insurance terms version.

~~~mermaid
erDiagram
    users ||--o{ policies : owns
    policies ||--o{ insured_persons : insures
    insurance_plans ||--o{ insurance_plan_versions : has_versions
    insurance_plan_versions ||--o{ plan_variants : offers
    plan_variants ||--o{ policies : selected_by
    plan_variants ||--o{ variant_coverages : defines
    coverage_types ||--o{ variant_coverages : classifies
    insurance_terms_versions ||--o{ policies : applies_to
    insurance_terms_versions ||--o{ knowledge_documents : documents

    users {
        integer id PK
        uuid auth_user_id UK "nullable"
        varchar email UK "max 255"
    }

    policies {
        integer id PK
        varchar policy_number UK "max 50"
        integer user_id FK
        integer plan_variant_id FK
        integer terms_version_id FK
        varchar trip_purpose "max 50"
        varchar declared_sport_category "max 50"
        date start_date
        date end_date
        timestamptz issued_at
        varchar status "max 30"
        numeric price_paid "12,2"
        varchar currency "max 3"
        timestamptz created_at
        timestamptz updated_at
    }

    insured_persons {
        integer id PK
        integer policy_id FK
        varchar name "max 150"
        date date_of_birth
    }

    insurance_plans {
        integer id PK
        varchar name UK "max 50"
    }

    insurance_plan_versions {
        integer id PK
        integer plan_id FK
        integer version
        date available_from
        date available_to "nullable"
    }

    plan_variants {
        integer id PK
        integer plan_version_id FK
        varchar territory "max 30"
    }

    coverage_types {
        integer id PK
        varchar code UK "max 50"
        varchar name "max 150"
    }

    variant_coverages {
        integer id PK
        integer plan_variant_id FK
        integer coverage_type_id FK
        numeric limit_amount "15,2"
        varchar currency "max 3"
    }

    insurance_terms_versions {
        integer id PK
        varchar code UK "max 50"
        date valid_from
        date valid_to "nullable"
    }

    knowledge_documents {
        integer id PK
        integer terms_version_id FK
        varchar title "max 255"
        varchar file_name "max 255"
        varchar storage_path UK "max 500"
        varchar checksum UK "max 64"
        varchar processing_status "max 20"
        timestamptz created_at
    }
~~~

## How a policy gets its coverage

A policy's plan_variant_id points to a territory such as Europe. That variant belongs to one insurance_plan_version, which belongs to a tier such as Dominant. The variant's variant_coverages rows provide the limits for that exact release and territory.

The plan version's available_from and available_to dates define when that release can be issued. policies.issued_at records when the policy was issued. The policy keeps the chosen variant ID, so a later release with changed limits does not change the policy's recorded benefit schedule. Travel dates (start_date and end_date) remain separate.

The policy also stores terms_version_id directly. Legal wording can therefore be versioned independently of benefit limits. knowledge_documents point to their terms version for retrieval.

Sport and trip purpose are policy-level declarations. They do not select a different benefit schedule in this model. Czech domestic coverages use the recreational limits selected by the user; sport-specific exclusions or eligibility remain in the policy terms.

## Key constraints

- Unique fields: user email and auth user ID; policy number; plan name; terms-version code; coverage-type code; document storage path and checksum.
- Composite unique constraints: plan version on (plan_id, version); plan variant on (plan_version_id, territory); variant coverage on (plan_variant_id, coverage_type_id).
- users.auth_user_id is a nullable UUID mapped to Supabase Auth; the database does not define a foreign key to Supabase's auth schema.
- insurance_plan_versions.available_from/available_to describe the product release's issue availability, not the insured trip dates.
- Seed data is for the demo catalogue. Coverage rows for a variant referenced by a policy cannot be inserted, updated, or deleted; create a new plan version and variant when limits change.
- Migration `e91a6c4b7d20` consolidates legacy sport-specific variants for every plan-version/territory group, preferring the recreational schedule when present. It cannot be downgraded to the previous differing sport schedules.
- knowledge_documents stores document metadata and processing status. Document chunks, embeddings, conversations, messages, and citations are not yet implemented.
