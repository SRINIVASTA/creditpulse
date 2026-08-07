import streamlit as st

class ImmutableAuditLogger:
    def log_decision(self, account_id, pd_val, ecl_val, tag):
        """Simulates recording immutable ledger blocks for central compliance auditing."""
        # Kept abstract to prevent disk space overflows during live multi-user dashboard instances
        pass
