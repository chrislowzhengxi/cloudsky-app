# CloudySky ER Diagram

||--|| → one-to-one

||--|{ → one-to-many (required FK)

||--o{ → one-to-many (optional FK)

o{--o{ → many-to-many

o-- → zero-to


```mermaid
erDiagram
    User {
        int id PK
        string username
    }

    Profile {
        int id PK
        int user FK
        string user_type
        string bio
        string avatar
    }

    Post {
        int id PK
        int author FK
        string content
        datetime created_at
        bool is_hidden
        int moderator FK
        int moderation_reason FK
    }

    Comment {
        int id PK
        int post FK
        int author FK
        string content
        datetime created_at
        bool is_hidden
        int moderator FK
        int moderation_reason FK
    }

    ModerationReason {
        int id PK
        string reason_text
    }

    Media {
        int id PK
        int uploader FK
        string file
        datetime uploaded_at
        int post FK
        int comment FK
    }

    %% Relationships
    User ||--|| Profile : has
    User ||--o{ Post : authors
    User ||--o{ Comment : authors
    User ||--o{ Media : uploads
    User ||--o{ Post : moderates
    User ||--o{ Comment : moderates
    Post ||--|{ Comment : contains
    Post |o--|{ Media : attaches
    Comment |o--|{ Media : attaches
    ModerationReason ||--o{ Post : explains
    ModerationReason ||--o{ Comment : explains
