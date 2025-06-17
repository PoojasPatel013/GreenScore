import streamlit as st
from datetime import datetime
from backend.mock_transaction import MockTransaction

mock_transaction = MockTransaction()

def transaction_form():
    """Streamlit component for manual transaction input"""
    st.header("Add Transaction")
    
    with st.form("transaction_form"):
        amount = st.number_input("Amount", min_value=0.01, value=10.0, step=0.01)
        description = st.text_input("Description", "Enter transaction description")
        
        category = st.selectbox(
            "Category",
            [
                "Transport",
                "Food & Dining",
                "Utilities",
                "Shopping",
                "Other"
            ]
        )
        
        submitted = st.form_submit_button("Add Transaction")
        
        if submitted:
            if not description:
                st.error("Please enter a description")
                return
            
            transaction = mock_transaction.add_transaction({
                'description': description,
                'amount': amount,
                'category': category.lower().replace(' & ', '_')
            })
            
            st.success("Transaction added successfully!")
            st.write(transaction)
            st.experimental_rerun()
