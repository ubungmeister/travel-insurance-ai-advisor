package com.aiadvisor;

import javax.sql.DataSource;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.condition.ConditionalOnExpression;
import org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;

import com.zaxxer.hikari.HikariDataSource;

// DataSource is wired manually so the app still boots when DB env vars are unset
// (Phase 0). Auto-configuration is re-enabled once JPA lands in Phase 1.
@SpringBootApplication(exclude = DataSourceAutoConfiguration.class)
public class AiAdvisorApplication {

    public static void main(String[] args) {
        SpringApplication.run(AiAdvisorApplication.class, args);
    }

    @Bean
    @ConditionalOnExpression("'${SPRING_DATASOURCE_URL:}' != ''")
    DataSource dataSource(
            @Value("${SPRING_DATASOURCE_URL}") String url,
            @Value("${SPRING_DATASOURCE_USERNAME:}") String username,
            @Value("${SPRING_DATASOURCE_PASSWORD:}") String password) {
        HikariDataSource ds = new HikariDataSource();
        ds.setJdbcUrl(url);
        ds.setUsername(username);
        ds.setPassword(password);
        // Don't abort startup if the DB is unreachable; /health/db reports it instead.
        ds.setInitializationFailTimeout(-1);
        return ds;
    }
}
