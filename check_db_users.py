import sqlite3

def check_users():
    conn = sqlite3.connect('leitor_inteligente_v2.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, hashed_password, is_active FROM usuarios")
    users = cursor.fetchall()
    print("Users in DB:")
    for user in users:
        print(user)
    conn.close()

if __name__ == "__main__":
    check_users()
