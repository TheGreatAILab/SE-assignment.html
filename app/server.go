package main

import (
	"encoding/json"
	"fmt"
	"math/rand"
	"net/http"
	"os"

	"github.com/labstack/echo/v4"
)

type StudentData map[string]string

func main() {
	e := echo.New()
	e.GET("/", func(ctx echo.Context) error {
		return ctx.File("index.html")
	})
	e.GET("/random", getHandler)
	e.Logger.Fatal(e.Start(":1323"))
}

func getHandler(ctx echo.Context) error {
	filePath := "data/students.json" // path to json
	data, err := random_get_data(filePath)
	if err != nil {
		panic(err)
	}
	return ctx.JSON(http.StatusOK, data)
}

func random_get_data(filepath string) (map[string]string, error) {
	content, err := os.ReadFile(filepath)
	if err != nil {
		panic(err)
	}

	var data StudentData
	err = json.Unmarshal(content, &data)
	if err != nil {
		panic(err)
	}

	if len(data) == 0 {
		return nil, fmt.Errorf("JSON %s is empty", filepath)
	}

	names := make([]string, 0, len(data))
	for name := range data {
		names = append(names, name)
	}

	index := rand.Intn(len(names))
	randomName := names[index]
	randomID := data[randomName]

	result := map[string]string{
		"name": randomName,
		"id":   randomID,
	}

	return result, nil
}
