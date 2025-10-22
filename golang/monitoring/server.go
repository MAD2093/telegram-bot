package monitoring

import (
	"log"
	"net/http"

	"github.com/prometheus/client_golang/prometheus/promhttp"
)

func StartMetricsServer(port string) {
	http.Handle("/metrics", promhttp.Handler())
	
	log.Printf("Starting metrics server on port %s", port)
	if err := http.ListenAndServe(":"+port, nil); err != nil {
		log.Fatalf("Error starting metrics server: %v", err)
	}
} 