import sys
from PyQt6 import QtWidgets
from PyQt6.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Carnet d'Adresses")
        self.setGeometry(100, 100, 800, 600)

        # Initialiser la base de données #
        self.initialize_db()

        # Configurer le modèle et la vue pour afficher les contacts #
        self.model = QSqlTableModel(self)
        self.model.setTable("contacts")
        self.model.select()

        # Créer une vue de table pour afficher les contacts #
        self.table_view = QtWidgets.QTableView(self)
        self.table_view.setModel(self.model)
        self.setCentralWidget(self.table_view)

        # Champs d'entrée pour ajouter/modifier un contact #
        self.nom_input = QtWidgets.QLineEdit(self)
        self.prenom_input = QtWidgets.QLineEdit(self)
        self.tel_prof_input = QtWidgets.QLineEdit(self)
        self.tel_port_input = QtWidgets.QLineEdit(self)
        self.tel_pers_input = QtWidgets.QLineEdit(self)
        self.email_input = QtWidgets.QLineEdit(self)

        # Boutons pour les actions #
        self.add_button = QtWidgets.QPushButton("Ajouter Contact", self)
        self.modify_button = QtWidgets.QPushButton("Modifier Contact", self)
        self.delete_button = QtWidgets.QPushButton("Supprimer Contact", self)
        self.refresh_button = QtWidgets.QPushButton("Actualiser", self)  # Bouton Actualiser
        self.reset_button = QtWidgets.QPushButton("Initialiser Base de Données", self)  # Nouveau bouton

        # Champ de recherche #
        self.search_input = QtWidgets.QLineEdit(self)

        # Layout pour les champs et boutons #
        layout = QtWidgets.QFormLayout()

        # Ajouter des champs d'entrée au layout #
        layout.addRow("Nom:", self.nom_input)
        layout.addRow("Prénom:", self.prenom_input)
        layout.addRow("Tel Professionnel:", self.tel_prof_input)
        layout.addRow("Tel Portable:", self.tel_port_input)
        layout.addRow("Tel Personnel:", self.tel_pers_input)
        layout.addRow("E-mail:", self.email_input)

        # Ajouter les boutons au layout #
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.modify_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.refresh_button)  # Bouton Actualiser #
        button_layout.addWidget(self.reset_button)  # Ajouter le bouton à l'interface #

        layout.addRow(button_layout)

        # Champ de recherche pour filtrer les contacts #
        layout.addRow("Recherche:", self.search_input)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)

        # Ajouter le widget au QMainWindow #
        self.setMenuWidget(widget)

        # Connecter les boutons à leurs fonctions respectives #
        self.add_button.clicked.connect(self.add_contact)
        self.modify_button.clicked.connect(self.modify_contact)  # Connexion du bouton modifier #
        self.delete_button.clicked.connect(self.delete_contact)

        # Connecter le bouton d'actualisation à sa fonction #
        self.refresh_button.clicked.connect(self.refresh_data)

        # Connecter le bouton d'initialisation à sa fonction #
        self.reset_button.clicked.connect(self.reset_database)

        # Connecter la barre de recherche pour filtrer les contacts #
        self.search_input.textChanged.connect(self.search_contacts)  # Utiliser textChanged #

        # Connecter la sélection d'un contact pour pré-remplir les champs d'entrée lors de la modification #
        self.table_view.selectionModel().selectionChanged.connect(self.fill_inputs)

    def initialize_db(self):
        """Initialise la base de données SQLite."""

        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName("carnet_adresses.db")  # Nom du fichier de base de données #

        if not db.open():
            QtWidgets.QMessageBox.critical(self, "Erreur", "Impossible de se connecter à la base de données.")
            return

        # Configurer l'environnement et créer les tables si elles n'existent pas #
        self.setup_database()

    def setup_database(self):
        """Configure l'environnement et crée les tables nécessaires."""

        # Créer la table des contacts si elle n'existe pas #
        self.create_table()

    def create_table(self):
        """Crée la table des contacts dans la base de données."""

        query = QSqlQuery()

        query.exec('''
                 CREATE TABLE IF NOT EXISTS contacts (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     nom TEXT NOT NULL,
                     prenom TEXT NOT NULL,
                     tel_professionnel TEXT,
                     tel_portable TEXT,
                     tel_personnel TEXT,
                     email TEXT
                 )
             ''')

    def add_contact(self):
        """Ajoute un nouveau contact à la base de données."""

        nom = self.nom_input.text().strip()
        prenom = self.prenom_input.text().strip()

        # Vérification des champs obligatoires #
        if not nom or not prenom:
            QtWidgets.QMessageBox.warning(self, "Erreur", "Nom et Prénom sont obligatoires.")
            return

        if not (self.tel_prof_input.text() or
                self.tel_port_input.text() or
                self.tel_pers_input.text() or
                self.email_input.text()):
            QtWidgets.QMessageBox.warning(self, "Erreur", "Au moins un numéro ou email doit être renseigné.")
            return

        query = QSqlQuery()

        query.prepare('''
                 INSERT INTO contacts (nom, prenom, tel_professionnel, tel_portable, tel_personnel, email) 
                 VALUES (?, ?, ?, ?, ?, ?)
             ''')

        query.addBindValue(nom)
        query.addBindValue(prenom)
        query.addBindValue(self.tel_prof_input.text())
        query.addBindValue(self.tel_port_input.text())
        query.addBindValue(self.tel_pers_input.text())
        query.addBindValue(self.email_input.text())

        if query.exec():
            QtWidgets.QMessageBox.information(self, "Succès", "Contact ajouté avec succès.")
            self.model.select()  # Rafraîchir la vue après ajout #
            self.clear_inputs()

    def modify_contact(self):
        """Modifie un contact existant dans la base de données."""

        selected_row = self.table_view.currentIndex().row()

        if selected_row < 0:
            QtWidgets.QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un contact à modifier.")
            return

        contact_id = int(self.model.index(selected_row, 0).data())  # ID du contact sélectionné

        nom = self.nom_input.text().strip()
        prenom = self.prenom_input.text().strip()

        # Vérification des champs obligatoires lors de la modification #
        if not nom or not prenom:
            QtWidgets.QMessageBox.warning(self, "Erreur", "Nom et Prénom sont obligatoires.")
            return

        if not (self.tel_prof_input.text() or
                self.tel_port_input.text() or
                self.tel_pers_input.text() or
                self.email_input.text()):
            QtWidgets.QMessageBox.warning(self, "Erreur", "Au moins un numéro ou email doit être renseigné.")
            return

        query = QSqlQuery()

        query.prepare('''
                  UPDATE contacts SET nom=?, prenom=?, tel_professionnel=?, tel_portable=?, tel_personnel=?, email=? WHERE id=?
              ''')

        query.addBindValue(nom)
        query.addBindValue(prenom)
        query.addBindValue(self.tel_prof_input.text())
        query.addBindValue(self.tel_port_input.text())
        query.addBindValue(self.tel_pers_input.text())
        query.addBindValue(self.email_input.text())
        query.addBindValue(contact_id)

        if query.exec():
            QtWidgets.QMessageBox.information(self, "Succès", "Contact modifié avec succès.")
            self.model.select()  # Rafraîchir la vue après modification
            self.clear_inputs()

    def delete_contact(self):
        """Supprime un contact sélectionné de la base de données."""
        selected_row = self.table_view.currentIndex().row()

        if selected_row < 0:
            QtWidgets.QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un contact à supprimer.")
            return

        contact_id = int(self.model.index(selected_row, 0).data())  # ID du contact sélectionné

        confirmation = QtWidgets.QMessageBox.question(
            self,
            "Confirmation",
            "Êtes-vous sûr de vouloir supprimer ce contact ?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.No
        )

        if confirmation == QtWidgets.QMessageBox.StandardButton.Yes:
            query = QSqlQuery()
            query.prepare('DELETE FROM contacts WHERE id=?')
            query.addBindValue(contact_id)

            if query.exec():
                QtWidgets.QMessageBox.information(self, "Succès", "Contact supprimé avec succès.")
                self.model.select()  # Rafraîchir la vue après suppression
                self.clear_inputs()  # Vider les champs après suppression

    def reset_database(self):
        """Réinitialise la base de données en supprimant tous les contacts."""

        confirmation = QtWidgets.QMessageBox.question(
            self,
            "Confirmation",
            "Êtes-vous sûr de vouloir initialiser la base de données ?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.No
        )

        if confirmation == QtWidgets.QMessageBox.StandardButton.Yes:
            query = QSqlQuery()

            # Supprimer la table si elle existe déjà et recréer une nouvelle table.#
            query.exec('DROP TABLE IF EXISTS contacts')

            # Recréer la table vide.#
            self.create_table()

            QtWidgets.QMessageBox.information(self, "Succès", "Base de données réinitialisée avec succès.")
            self.model.select()  # Rafraîchir la vue

    def refresh_data(self):
        """Rafraîchit les données affichées dans le tableau."""

        print("Données rafraîchies.")  # Debug: Afficher que l'actualisation a été appelée.#
        if not self.model.select():  # Tentez de recharger les données.
            print("Erreur lors du rafraîchissement des données.")  # Debug: Afficher une erreur si le chargement échoue#

        else:
            QtWidgets.QMessageBox.information(self, "Actualisation",
                                              "Les données ont été actualisées.")  # Message après actualisation#

    def search_contacts(self):
        """Filtre les contacts en fonction de la recherche."""

        search_text = self.search_input.text().strip()

        if search_text:
            filter_string = f"nom LIKE '%{search_text}%' OR prenom LIKE '%{search_text}%'"
            print(filter_string)  # Debug: Afficher le filtre dans la console#
            self.model.setFilter(filter_string)  # Appliquer le filtre sur le modèle #
        else:
            print("Aucun filtre appliqué.")  # Debug: Aucune recherche active#
            self.model.setFilter("")  # Afficher tous les contacts #

    def clear_inputs(self):
        """Efface les champs d'entrée."""

        print("Champs effacés.")  # Debug: Afficher que les champs sont effacés#
        self.nom_input.clear()
        self.prenom_input.clear()
        self.tel_prof_input.clear()
        self.tel_port_input.clear()
        self.tel_pers_input.clear()
        self.email_input.clear()

    def fill_inputs(self):
        """Remplit les champs d'entrée avec les informations du contact sélectionné."""
        selected_row = self.table_view.currentIndex().row()
        if selected_row >= 0:
            contact_id = int(self.model.index(selected_row, 0).data())  # ID du contact sélectionné

            nom = str(self.model.index(selected_row, 1).data())  # Récupérer le nom
            prenom = str(self.model.index(selected_row, 2).data())  # Récupérer le prénom
            tel_professionnel = str(self.model.index(selected_row, 3).data())  # Récupérer le téléphone professionnel
            tel_portable = str(self.model.index(selected_row, 4).data())  # Récupérer le téléphone portable
            tel_personnel = str(self.model.index(selected_row, 5).data())  # Récupérer le téléphone personnel
            email = str(self.model.index(selected_row, 6).data())  # Récupérer l'email

            # Remplir les champs d'entrée avec ces valeurs #
            print(
                f"Remplissage des champs: {nom}, {prenom}, {tel_professionnel}, {tel_portable}, {tel_personnel}, {email}")  # Debug: Afficher les valeurs remplies.
            self.nom_input.setText(nom)
            self.prenom_input.setText(prenom)
            self.tel_prof_input.setText(tel_professionnel)
            self.tel_port_input.setText(tel_portable)
            self.tel_pers_input.setText(tel_personnel)
            self.email_input.setText(email)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)  # Créer l'application PyQt6 #
    window = MainWindow()  # Créer une instance de MainWindow #
    window.show()  # Afficher la fenêtre principale #
    sys.exit(app.exec())  # Exécuter l'application et attendre sa fermeture #
