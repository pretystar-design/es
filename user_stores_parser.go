package main

import (
    "bufio"
    "fmt"
    "log"
    "os"
    "strings"
)

// Simple CLI to list user stories from user_stores.md.
// Usage: go run . user_stores_parser.go [list|backlog]
func main() {
    if len(os.Args) < 2 {
        fmt.Println("Usage: go run user_stores_parser.go [list|backlog]")
        os.Exit(1)
    }
    mode := os.Args[1]
    f, err := os.Open("user_stores.md")
    if err != nil {
        log.Fatalf("failed to open user_stores.md: %v", err)
    }
    defer f.Close()
    scanner := bufio.NewScanner(f)
    switch mode {
    case "list":
        fmt.Println("User Stories:")
        for scanner.Scan() {
            line := scanner.Text()
            // Detect lines that start with a number and a dot (e.g., "1. 基础资源编辑")
            if strings.HasPrefix(line, "#") || strings.TrimSpace(line) == "" {
                continue
            }
            if parts := strings.SplitN(line, ".", 2); len(parts) == 2 {
                if _, err := fmt.Sscanf(strings.TrimSpace(parts[0]), "%d", new(int)); err == nil {
                    fmt.Printf("- %s\n", strings.TrimSpace(parts[1]))
                }
            }
        }
    case "backlog":
        fmt.Println("Backlog Table:")
        // Find the markdown table header and rows
        inTable := false
        for scanner.Scan() {
            line := scanner.Text()
            if strings.HasPrefix(line, "| ID") {
                fmt.Println(line)
                inTable = true
                continue
            }
            if inTable {
                if strings.HasPrefix(line, "|---") {
                    fmt.Println(line)
                    continue
                }
                if strings.HasPrefix(line, "|") {
                    fmt.Println(line)
                } else {
                    // End of table
                    break
                }
            }
        }
    default:
        fmt.Println("Unknown mode. Use 'list' or 'backlog'.")
    }
    if err := scanner.Err(); err != nil {
        log.Fatalf("scanner error: %v", err)
    }
}
