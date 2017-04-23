package sensor.server.process.retrieve.activemq;

import javax.jms.ConnectionFactory;
import javax.jms.Topic;

import org.apache.activemq.command.ActiveMQTopic;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.jms.DefaultJmsListenerContainerFactoryConfigurer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.jms.config.DefaultJmsListenerContainerFactory;
import org.springframework.jms.config.JmsListenerContainerFactory;

@Configuration
public class ActiveMqConfiguration {
	private static final Logger LOGGER = LoggerFactory.getLogger(ActiveMqConfiguration.class);

	public static String TOPIC_NAME;
	public static String TOPIC_CLIENT_ID;
	public static String TOPIC_SUBSCRIPTION;
	public static final String DURABLE_SUBSCRIPTION = "durableSubscriptionJmsListener";
	public static final String PROPERTY_TOPIC_NAME = "${sensor.server.activemq.topic.name}";
	public static final String PROPERTY_TOPIC_CLIENT_ID = "${sensor.server.activemq.topic.clientid}";
	public static final String PROPERTY_TOPIC_SUBSCRIPTION = "${sensor.server.activemq.topic.subscription}";

	@Value(PROPERTY_TOPIC_NAME)
	public void setTopicName(String topicName) {
		TOPIC_NAME = topicName;
	}

	@Value(PROPERTY_TOPIC_CLIENT_ID)
	public void setTopicClientId(String topicClientId) {
		TOPIC_CLIENT_ID = topicClientId;
	}

	@Value(PROPERTY_TOPIC_SUBSCRIPTION)
	public void setTopicSubscription(String topicSubscription) {
		TOPIC_SUBSCRIPTION = topicSubscription;
	}

	@Bean
	public Topic activeMqTopic() {
		LOGGER.debug("Initializing active mq topic {}, clientId {}, subscription {}", TOPIC_NAME, TOPIC_CLIENT_ID,
				TOPIC_SUBSCRIPTION);
		return new ActiveMQTopic(TOPIC_NAME);
	}

	@Bean(name = DURABLE_SUBSCRIPTION)
	public JmsListenerContainerFactory<?> durableSubscriptionJmsListenerContainerFactory(
			ConnectionFactory connectionFactory, DefaultJmsListenerContainerFactoryConfigurer configurer) {
		DefaultJmsListenerContainerFactory factory = new DefaultJmsListenerContainerFactory();
		configurer.configure(factory, connectionFactory);
		factory.setPubSubDomain(true);
		factory.setClientId(TOPIC_CLIENT_ID);
		factory.setSubscriptionDurable(true);
		return factory;
	}
}
