import streamlit_authenticator as stauth

hashed_passwords = stauth.Hasher(["YOUR_PASSWORD"]).generate()
print(hashed_passwords)
