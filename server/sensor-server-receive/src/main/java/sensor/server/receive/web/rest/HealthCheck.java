package sensor.server.receive.web.rest;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * Kubernetes "Ingress" uses request to root path to check if service is healthy
 * and expects a HTTP/200 response.
 */
@RestController
@RequestMapping("/")
public class HealthCheck {

	@GetMapping
	public String ping() {
		return "";
	}
}