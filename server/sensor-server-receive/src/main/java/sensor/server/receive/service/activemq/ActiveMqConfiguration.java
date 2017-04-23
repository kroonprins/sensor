package sensor.server.receive.service.activemq;

import javax.jms.Topic;

import org.apache.activemq.command.ActiveMQTopic;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class ActiveMqConfiguration {
	private static final Logger LOGGER = LoggerFactory.getLogger(ActiveMqConfiguration.class);

	public static String TOPIC;

	@Value("${sensor.server.activemq.topic.name}")
	public void setTopic(String topic) {
		TOPIC = topic;
	}

	@Bean
	public Topic activeMqTopic() {
		LOGGER.debug("Initializing active mq topic {}", TOPIC);
		return new ActiveMQTopic(TOPIC);
	}
}
