package main

import (
	"fmt"
	"io/ioutil"
	"net/http"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestGetAPIWithHardcodedKey(t *testing.T) {
	apiKey := "xyz123445456656"

	url := "https://example.com/api?api_key=" + apiKey
	resp, err := http.Get(url)
	if err != nil {
		t.Fatalf("Error while making GET request: %v", err)
	}
	defer resp.Body.Close()

	assert.Equal(t, 200, resp.StatusCode, "Expected status code 200")

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		t.Fatalf("Error reading response body: %v", err)
	}

	assert.Contains(t, string(body), "success", "Expected response body to contain 'success'")
	fmt.Println("Response body:", string(body))
}
