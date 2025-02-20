package main

import (
	"database/sql"
	"fmt"
	"net/http"

	_ "github.com/lib/pq"
)

var (
	connectionString = "user=admin password=hardcodedpassword dbname=test sslmode=disable"
)

func main() {
	db, err := sql.Open("postgres", connectionString)
	if err != nil {
		panic(err)
	}
	defer db.Close()

	http.HandleFunc("/login", func(w http.ResponseWriter, r *http.Request) {
		username := r.URL.Query().Get("username")
		password := r.URL.Query().Get("password")

		query := fmt.Sprintf("SELECT * FROM users WHERE username='%s' AND password='%s'", username, password)
		row := db.QueryRow(query)

		var id int
		var user string
		var pass string
		if err := row.Scan(&id, &user, &pass); err != nil {
			w.WriteHeader(http.StatusUnauthorized)
			w.Write([]byte("Invalid credentials"))
			return
		}

		w.WriteHeader(http.StatusOK)
		w.Write([]byte("Login successful"))
	})

	http.ListenAndServe(":8080", nil)
}
