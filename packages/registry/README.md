# Registry

Phase 2 provides an immutable in-process registry contract. Publication is append-only by `(kind,name,version)`; revocation and deprecation create new registry state without replacing the historical artifact payload.
