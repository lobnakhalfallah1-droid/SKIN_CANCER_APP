from flask import Flask, render_template, request, redirect, session, flash, url_for
import os
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import mysql.connector
from dotenv import load_dotenv
from groq import Groq

app = Flask(__name__)
app.secret_key = "secret"

UPLOAD_FOLDER = "static/uploads/"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

model = load_model("model/vgg16_malignant_vs_benign.h5")

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="skin_cancer_db"
)

cursor = db.cursor(dictionary=True)

@app.before_request
def check_db_connection():
    global db, cursor
    try:
        db.ping(reconnect=True, attempts=3, delay=1)
        cursor = db.cursor(dictionary=True)
    except Exception as e:
        print("Tentative de reconnexion BDD échouée :", e)

try:
    cursor.execute("ALTER TABLE patients ADD COLUMN email VARCHAR(255) NULL AFTER age")
    db.commit()
    print("Colonne 'email' ajoutée à la table patients avec succès.")
except Exception as e:
    # L'erreur (1060, "Duplicate column name 'email'") est attendue si la colonne existe déjà
    pass

# Charger les variables d'environnement
env_path = os.path.join(os.path.dirname(__file__), 'templates', '.env')
load_dotenv(env_path)
groq_api_key = os.getenv("GROQ_API_KEY")

try:
    groq_client = Groq(api_key=groq_api_key)
except Exception as e:
    print("Erreur d'initialisation Groq:", e)
    groq_client = None


# ---------------- LANDING PAGE ----------------
@app.route("/")
def index():
    return render_template("landing.html")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form.get("username")
        pwd = request.form.get("password")

        cursor.execute("SELECT * FROM users WHERE username=%s", (user,))
        existing_user = cursor.fetchone()

        if not existing_user:
            flash(f"L'identifiant « {user} » n'existe pas. Créez votre compte.", "warning")
            return redirect(url_for("signup"))

        cursor.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (user, pwd)
        )
        result = cursor.fetchone()

        if result:
            session["user"] = result["username"]
            session["role"] = result.get("role", "Médecin")
            return redirect(url_for("dashboard"))
        else:
            flash("Mot de passe incorrect ✖", "danger")

    return render_template("login.html")


# ---------------- SIGNUP ----------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        role = request.form.get("role", "autre").strip()

        if role == "autre":
            role_custom = request.form.get("role_custom", "").strip()
            if role_custom:
                role = role_custom

        pwd = request.form.get("password", "")
        confirm_pwd = request.form.get("confirm_password", "")

        errors = []

        if not all([first_name, last_name, username, email, pwd]):
            errors.append("Tous les champs sont obligatoires.")

        if len(username) < 3:
            errors.append("L'identifiant doit contenir au moins 3 caractères.")

        import re
        if len(pwd) < 8:
            errors.append("Le mot de passe doit contenir au moins 8 caractères.")
        elif not re.search(r"[A-Z]", pwd):
            errors.append("Le mot de passe doit contenir au moins une lettre majuscule.")
        elif not re.search(r"[a-z]", pwd):
            errors.append("Le mot de passe doit contenir au moins une lettre minuscule.")
        elif not re.search(r"[0-9]", pwd):
            errors.append("Le mot de passe doit contenir au moins un chiffre.")
        elif not re.search(r"[\W_]", pwd):
            errors.append("Le mot de passe doit contenir au moins un caractère spécial.")

        if pwd != confirm_pwd:
            errors.append("Les mots de passe ne correspondent pas.")

        cursor.execute("SELECT id FROM users WHERE username=%s", (username,))
        if cursor.fetchone():
            errors.append(f"L'identifiant « {username} » est déjà utilisé.")

        cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
        if cursor.fetchone():
            errors.append("Cette adresse e-mail est déjà associée à un compte.")

        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template("signup.html")

        cursor.execute("""
            INSERT INTO users (username, password, first_name, last_name, email, role)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (username, pwd, first_name, last_name, email, role))

        db.commit()

        session["user"] = username
        session["role"] = role

        flash(f"Bienvenue, {first_name} ! Votre compte a été créé. ✔", "success")
        return redirect(url_for("dashboard"))

    return render_template("signup.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    cursor.execute("SELECT COUNT(*) AS total FROM patients")
    patients_count = cursor.fetchone()["total"]

    analyses_count = patients_count
    cursor.execute("SELECT COUNT(*) as count FROM patients WHERE result = 'Malignant'")
    critical_count = cursor.fetchone()["count"]

    cursor.execute("""
        SELECT id, name, age, email, result, probability, image_path
        FROM patients
        WHERE result = 'Malignant' OR probability >= 0.50
        ORDER BY probability DESC
        LIMIT 3
    """)
    priority_patients = cursor.fetchall()

    priority_count = len(priority_patients)

    notifications = []

    if priority_count > 0:
        notifications.append({
            "title": "Priorité IA",
            "message": f"{priority_count} patient(s) nécessitent une attention.",
            "type": "warning",
            "is_read": False
        })

    if patients_count > 0:
        notifications.append({
            "title": "Analyses disponibles",
            "message": f"{patients_count} patient(s) enregistré(s).",
            "type": "success",
            "is_read": False
        })
    else:
        notifications.append({
            "title": "Bienvenue",
            "message": "Commencez par ajouter une première analyse.",
            "type": "info",
            "is_read": False
        })

    notif_unread = sum(1 for n in notifications if not n["is_read"])

    return render_template(
        "dashboard.html",
        analyses_count=analyses_count,
        critical_count=critical_count,
        patients_count=patients_count,
        notifications=notifications,
        notif_unread=notif_unread,
        priority_patients=priority_patients
    )


# ---------------- PREDICTION ----------------
@app.route("/predict", methods=["GET", "POST"])
def predict():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        try:
            name = request.form["name"]
            age = request.form["age"]
            email = request.form.get("email", "")
            file = request.files["image"]

            if file.filename == "":
                flash("Veuillez choisir une image.", "warning")
                return redirect(url_for("predict"))

            filename = file.filename
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(path)

            db_path = "/" + path.replace("\\", "/")

            img = image.load_img(path, target_size=(224, 224))
            img = image.img_to_array(img) / 255.0
            img = np.expand_dims(img, axis=0)

            pred = model.predict(img)[0][0]
            result = "Malignant" if pred > 0.5 else "Benign"
            probability = float(pred)

            cursor.execute("""
                INSERT INTO patients (name, age, email, result, probability, image_path)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name, age, email, result, probability, db_path))

            db.commit()

            flash("Analyse réussie ✔ Patient ajouté avec succès.", "success")
            return redirect(url_for("patients"))

        except Exception as e:
            print("Erreur predict :", e)
            flash(f"Erreur système : {e}", "danger")
            return redirect(url_for("predict"))

    return render_template("predict.html")


# ---------------- EMAIL AUTOMATIQUE ----------------
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

@app.route("/send-email/<int:patient_id>")
def send_patient_email(patient_id):
    if "user" not in session:
        return redirect(url_for("login"))
        
    cursor.execute("""
        SELECT name, email, result, probability
        FROM patients
        WHERE id = %s
    """, (patient_id,))
    patient = cursor.fetchone()
    
    if not patient:
        flash("Patient introuvable.", "danger")
        return redirect(url_for("dashboard"))
        
    if not patient.get("email"):
        flash("Ce patient n'a pas d'adresse email enregistrée.", "warning")
        return redirect(url_for("dashboard"))
        
    sender_email = os.getenv("EMAIL_USER")
    sender_password = os.getenv("EMAIL_PASS")
    receiver_email = patient["email"]
    
    if not sender_email or not sender_password or sender_email == "votre_adresse@gmail.com":
        flash("Configuration Email manquante. Veuillez configurer EMAIL_USER et EMAIL_PASS dans le fichier .env", "warning")
        return redirect(url_for("dashboard"))
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = "Convocation Médicale Importante - DermaVision"
    
    body = f"Bonjour {patient['name']},\n\nSuite à l'analyse de vos résultats dermatologiques récents, nous vous prions de bien vouloir nous contacter en urgence afin de programmer un rendez-vous médical de contrôle dans les plus brefs délais.\n\nCordialement,\nLe cabinet médical DermaVision"
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        flash(f"Email envoyé avec succès à {patient['email']}.", "success")
    except Exception as e:
        print("Erreur email:", e)
        flash(f"Erreur lors de l'envoi de l'email : {e}", "danger")
        
    return redirect(url_for("dashboard"))


# ---------------- PATIENTS ----------------
@app.route("/patients")
def patients():
    if "user" not in session:
        return redirect(url_for("login"))

    cursor.execute("SELECT id, name, age, email, result, probability, created_at, image_path FROM patients ORDER BY created_at DESC")
    data = cursor.fetchall()

    return render_template("patients.html", patients=data)


# ---------------- MODIFIER PATIENT ----------------
@app.route("/patients/edit/<int:patient_id>", methods=["GET", "POST"])
def edit_patient(patient_id):
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        age = request.form.get("age", "").strip()
        email = request.form.get("email", "").strip()

        if not name or not age:
            flash("Le nom et l'âge sont obligatoires.", "danger")
            return redirect(url_for("edit_patient", patient_id=patient_id))

        try:
            cursor.execute("""
                UPDATE patients SET name=%s, age=%s, email=%s WHERE id=%s
            """, (name, age, email, patient_id))
            db.commit()
            flash(f"Patient « {name} » mis à jour avec succès. ✔", "success")
        except Exception as e:
            print("Erreur modification patient:", e)
            flash("Erreur lors de la modification.", "danger")

        return redirect(url_for("patients"))

    cursor.execute("SELECT id, name, age, email, result, probability, image_path FROM patients WHERE id=%s", (patient_id,))
    patient = cursor.fetchone()

    if not patient:
        flash("Patient introuvable.", "danger")
        return redirect(url_for("patients"))

    return render_template("edit_patient.html", patient=patient)


# ---------------- SUPPRIMER PATIENT ----------------
@app.route("/patients/delete/<int:patient_id>", methods=["POST"])
def delete_patient(patient_id):
    if "user" not in session:
        return redirect(url_for("login"))

    try:
        cursor.execute("SELECT name, image_path FROM patients WHERE id=%s", (patient_id,))
        patient = cursor.fetchone()

        if not patient:
            flash("Patient introuvable.", "danger")
            return redirect(url_for("patients"))

        # Supprimer l'image uploadée si elle existe
        if patient.get("image_path"):
            img_path = patient["image_path"].lstrip("/")
            if os.path.exists(img_path):
                os.remove(img_path)

        cursor.execute("DELETE FROM patients WHERE id=%s", (patient_id,))
        db.commit()
        flash(f"Patient « {patient['name']} » supprimé avec succès.", "success")
    except Exception as e:
        print("Erreur suppression patient:", e)
        flash("Erreur lors de la suppression.", "danger")

    return redirect(url_for("patients"))


# ---------------- HISTORIQUE D'ANALYSES ----------------
@app.route("/patients/history/<int:patient_id>")
def patient_history(patient_id):
    if "user" not in session:
        return redirect(url_for("login"))

    cursor.execute("SELECT name FROM patients WHERE id=%s", (patient_id,))
    patient = cursor.fetchone()

    if not patient:
        flash("Patient introuvable.", "danger")
        return redirect(url_for("patients"))

    patient_name = patient["name"]

    cursor.execute("""
        SELECT id, name, age, email, result, probability, image_path, created_at
        FROM patients
        WHERE name = %s
        ORDER BY created_at DESC
    """, (patient_name,))
    analyses = cursor.fetchall()

    # Calculer les statistiques de l'historique
    total_analyses = len(analyses)
    malignant_count = sum(1 for a in analyses if a["result"] == "Malignant")
    benign_count = total_analyses - malignant_count
    avg_prob = sum(float(a["probability"]) for a in analyses) / total_analyses if total_analyses > 0 else 0

    stats = {
        "total": total_analyses,
        "malignant": malignant_count,
        "benign": benign_count,
        "avg_probability": round(avg_prob * 100, 1)
    }

    return render_template("patient_history.html",
                           patient_name=patient_name,
                           analyses=analyses,
                           stats=stats)


# ---------------- CHATBOT ----------------
@app.route("/chatbot")
def chatbot():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("chatbot.html")

@app.route("/api/chat", methods=["POST"])
def api_chat():
    if "user" not in session:
        return {"error": "Non autorisé"}, 401
    
    if not groq_client:
        return {"error": "L'API IA n'est pas configurée sur le serveur."}, 500
        
    data = request.json
    user_message = data.get("message", "")
    
    if not user_message:
        return {"error": "Le message est vide."}, 400
        
    user_name = session.get("user", "Docteur")
    role = session.get("role", "Médecin")
    
    # Récupérer les données des patients pour donner du contexte à l'IA
    try:
        cursor.execute("SELECT name, age, result, probability FROM patients ORDER BY id DESC LIMIT 50")
        patients_data = cursor.fetchall()
        
        patients_context = "=== BASE DE DONNÉES DES PATIENTS ===\n"
        if patients_data:
            for p in patients_data:
                prob = round(float(p['probability']) * 100, 2)
                patients_context += f"- Nom: {p['name']} | Âge: {p['age']} ans | Résultat IA: {p['result']} | Confiance: {prob}%\n"
        else:
            patients_context += "Aucun patient n'est actuellement enregistré.\n"
    except Exception as e:
        print("Erreur d'accès DB pour le chatbot:", e)
        patients_context = "Information: La base de données des patients est temporairement inaccessible.\n"
    
    system_prompt = f"""Tu es DermaAssist, un assistant médical IA extrêmement compétent spécialisé en dermatologie, intégré à la plateforme DermaVision.
L'utilisateur actuel est {user_name}, dont le rôle est {role}.

{patients_context}

Ton rôle est d'assister {user_name} avec des réponses précises, professionnelles et scientifiques sur des questions médicales, AINSI que de fournir des analyses sur les patients enregistrés.
Règles strictes :
1. Si l'utilisateur pose une question sur un patient (ex: "analyse les résultats de John"), cherche dans la base de données ci-dessus. Donne les informations du patient, explique la signification de son résultat (Benign = Bénin/sans danger grave, Malignant = Malin/suspect de cancer) et ce que le médecin devrait potentiellement faire (ex: recommandation de biopsie si Malin avec un score élevé).
2. Si le patient n'existe pas dans la base de données ci-dessus, dis-le clairement.
3. Si la question n'est pas liée au domaine médical ou aux patients de la plateforme, refuse poliment d'y répondre.
4. Garde tes réponses claires, concises et en français."""

    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3,
            max_tokens=1024,
            top_p=1,
            stream=False,
        )
        
        reply = completion.choices[0].message.content
        return {"reply": reply}
    except Exception as e:
        print("Erreur API Chatbot:", str(e))
        return {"error": "Une erreur est survenue lors de la réflexion de l'IA."}, 500


# ---------------- PAGES OPTIONNELLES ----------------
@app.route("/settings", methods=["GET", "POST"])
def settings():
    if "user" not in session:
        return redirect(url_for("login"))
        
    if request.method == "POST":
        action = request.form.get("action")
        user = session["user"]
        
        if action == "update_profile":
            new_username = request.form.get("username", "").strip()
            new_role = request.form.get("role", "").strip()
            
            if new_username:
                try:
                    # check if username already taken
                    if new_username != user:
                        cursor.execute("SELECT id FROM users WHERE username=%s", (new_username,))
                        if cursor.fetchone():
                            flash("Cet identifiant est déjà pris.", "danger")
                            return redirect(url_for("settings"))
                            
                    cursor.execute("UPDATE users SET username=%s, role=%s WHERE username=%s", (new_username, new_role, user))
                    db.commit()
                    
                    session["user"] = new_username
                    session["role"] = new_role
                    flash("Votre profil a été mis à jour avec succès.", "success")
                except Exception as e:
                    print("Erreur mise à jour profil:", e)
                    flash("Une erreur s'est produite lors de la mise à jour.", "danger")
                    
        elif action == "update_password":
            old_pwd = request.form.get("old_password")
            new_pwd = request.form.get("new_password")
            confirm_pwd = request.form.get("confirm_password")
            
            if new_pwd != confirm_pwd:
                flash("Les nouveaux mots de passe ne correspondent pas.", "danger")
            elif len(new_pwd) < 6:
                flash("Le mot de passe doit faire au moins 6 caractères.", "danger")
            else:
                try:
                    cursor.execute("SELECT password FROM users WHERE username=%s", (user,))
                    result = cursor.fetchone()
                    if result and result["password"] == old_pwd:
                        cursor.execute("UPDATE users SET password=%s WHERE username=%s", (new_pwd, user))
                        db.commit()
                        flash("Mot de passe mis à jour avec succès.", "success")
                    else:
                        flash("L'ancien mot de passe est incorrect.", "danger")
                except Exception as e:
                    print("Erreur mot de passe:", e)
                    flash("Une erreur s'est produite.", "danger")
                    
        return redirect(url_for("settings"))

    return render_template("settings.html")


@app.route("/help")
def help_page():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("help.html")


@app.route("/notifications")
def notifications_page():
    if "user" not in session:
        return redirect(url_for("login"))
    return "<h1>Page notifications bientôt disponible</h1><a href='/dashboard'>Retour</a>"


# ---------------- STATISTIQUES ----------------
@app.route("/stats")
def stats():
    if "user" not in session:
        return redirect(url_for("login"))

    try:
        cursor.execute("SELECT COUNT(*) AS total FROM patients")
        total_patients = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS count FROM patients WHERE result='Benign'")
        benign_count = cursor.fetchone()["count"]

        cursor.execute("SELECT COUNT(*) AS count FROM patients WHERE result='Malignant'")
        malignant_count = cursor.fetchone()["count"]
        
        cursor.execute("SELECT AVG(probability) AS avg_conf FROM patients")
        avg_prob = cursor.fetchone()["avg_conf"]
        avg_confidence = round(float(avg_prob) * 100, 1) if avg_prob else 0

    except Exception as e:
        print("Erreur Stats:", e)
        total_patients = benign_count = malignant_count = avg_confidence = 0

    return render_template("stats.html", 
                           total=total_patients, 
                           benign=benign_count, 
                           malignant=malignant_count,
                           avg_confidence=avg_confidence)


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    flash("Déconnecté", "info")
    return redirect(url_for("index"))


# ---------------- MAIN ----------------
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)