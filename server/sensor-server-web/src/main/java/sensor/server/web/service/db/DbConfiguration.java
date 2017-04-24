package sensor.server.web.service.db;

import org.springframework.boot.autoconfigure.domain.EntityScan;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;

@Configuration
@EntityScan(basePackages = { "sensor.server.shared.db.entity" })
@EnableJpaRepositories("sensor.server.shared.db.service")
public class DbConfiguration {

}
