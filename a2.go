package main

import (
	"database/sql"
	"fmt"
	"math/rand"
	"net/http"
	"os"
	"os/exec"

	_ "github.com/lib/pq"
)

func main() {
	http.HandleFunc("/login", func(w http.ResponseWriter, r *http.Request) {
		username := r.URL.Query().Get("username")
		password := r.URL.Query().Get("password")

		db, _ := sql.Open("postgres", "user=admin password=admin123 dbname=test sslmode=disable")
		query := fmt.Sprintf("SELECT * FROM users WHERE username='%s' AND password='%s'", username, password)
		rows, _ := db.Query(query)
		defer rows.Close()

		if rows.Next() {
			w.Write([]byte("Login successful"))
		} else {
			w.Write([]byte("Login failed"))
		}
	})

	http.HandleFunc("/run", func(w http.ResponseWriter, r *http.Request) {
		command := r.URL.Query().Get("cmd")
		output, _ := exec.Command(command).CombinedOutput()
		w.Write(output)
	})

	http.HandleFunc("/secret", func(w http.ResponseWriter, r *http.Request) {
		secret := "hardcoded_secret_key_12345"
		w.Write([]byte(secret))
	})

	http.HandleFunc("/random", func(w http.ResponseWriter, r *http.Request) {
		randomValue := rand.Int()
		w.Write([]byte(fmt.Sprintf("Random Value: %d", randomValue)))
	})

	http.HandleFunc("/env", func(w http.ResponseWriter, r *http.Request) {
		envVar := os.Getenv("SECRET_ENV_VAR")
		if envVar == "" {
			envVar = "default_secret_env"
		}
		w.Write([]byte(envVar))
	})

	http.ListenAndServe(":8080", nil)
}
