class SpringSecurityAnalyzer:
    def __init__(self):
        # Core configuration patterns that almost always contain sensitive data
        self.critical_patterns = {
            "credential_files": {
                "patterns": [
                    "**/application-prod.{properties,yml,yaml}",  # Production credentials
                    "**/application-staging.{properties,yml,yaml}",  # Staging credentials
                    "**/.env",  # Environment variables
                    "**/secrets.{properties,yml,yaml}",  # Explicit secrets files
                    "**/credentials.{properties,yml,yaml}",  # Additional credential files
                    "**/master.{properties,yml,yaml}",  # Master configuration files
                    "**/bootstrap-prod.{properties,yml,yaml}",  # Production bootstrap configs
                    "**/application-secure.{properties,yml,yaml}"  # Security-specific configs
                ],
                "risk_score": 10,
                "rationale": "Direct credential storage locations"
            },
            
            "security_configurations": {
                "patterns": [
                    "**/src/**/security/SecurityConfig.java",  # Spring Security config
                    "**/src/**/config/WebSecurityConfig.java",  # Web security settings
                    "**/src/**/security/JwtConfig.java",  # JWT configuration
                    "**/oauth2/*.{properties,yml,yaml}",  # OAuth2 settings
                    "**/saml/*.{properties,yml,yaml}",  # SAML configurations
                    "**/src/**/security/AuthorizationServerConfig.java",  # OAuth2 auth server
                    "**/src/**/security/ResourceServerConfig.java",  # OAuth2 resource server
                    "**/src/**/security/TokenConfig.java",  # Token management
                    "**/src/**/security/MethodSecurityConfig.java",  # Method-level security
                    "**/src/**/security/CorsSecurityConfig.java",  # CORS security
                    "**/src/**/security/SessionSecurityConfig.java",  # Session management
                    "**/src/**/security/SecurityBeanConfig.java"  # Security-related beans
                ],
                "risk_score": 9,
                "rationale": "Security framework configurations"
            },

            "encryption_materials": {
                "patterns": [
                    "**/*.{jks,keystore,truststore}",  # Java keystores
                    "**/*.{key,pem,crt,cer,p12}",  # Certificates and private keys
                    "**/keys/*.{properties,yml,yaml}",  # Encryption key configurations
                    "**/*.pfx",  # PKCS#12 archives
                    "**/*.der",  # DER-encoded certificates
                    "**/keystores/*.{properties,yml,yaml}",  # Keystore configurations
                    "**/certificates/*.{properties,yml,yaml}",  # Certificate configurations
                    "**/ssl/*.{properties,yml,yaml}"  # SSL/TLS configurations
                ],
                "risk_score": 10,
                "rationale": "Cryptographic materials"
            },

            "authentication_configurations": {
                "patterns": [
                    "**/src/**/security/LdapConfig.java",  # LDAP authentication
                    "**/src/**/security/OAuth2LoginConfig.java",  # OAuth2 login
                    "**/src/**/security/SamlConfig.java",  # SAML configuration
                    "**/src/**/security/KeycloakConfig.java",  # Keycloak integration
                    "**/src/**/security/OpenIdConfig.java",  # OpenID Connect
                    "**/src/**/security/AuthenticationConfig.java",  # Custom auth config
                    "**/src/**/security/MfaConfig.java",  # Multi-factor auth
                    "**/src/**/security/SocialLoginConfig.java",  # Social login
                    "**/authentication/*.{properties,yml,yaml}",  # Auth properties
                    "**/src/**/security/AuthProviderConfig.java"  # Custom auth providers
                ],
                "risk_score": 9,
                "rationale": "Authentication mechanism configurations"
            }
        }

        # Secondary patterns that might contain sensitive information
        self.high_risk_patterns = {
            "database_configs": {
                "patterns": [
                    "**/resources/application.{properties,yml,yaml}",  # Main application config
                    "**/META-INF/persistence.xml",  # JPA configuration
                    "**/hibernate.cfg.xml",  # Hibernate configuration
                    "**/flyway.{properties,yml,yaml}",  # Database migration config
                    "**/liquibase/*.{xml,yaml,sql}",  # Database changelog
                    "**/src/**/repository/CustomRepositoryConfig.java",  # Custom repo configs
                    "**/src/**/config/DataSourceConfig.java",  # DataSource configuration
                    "**/src/**/config/JpaConfig.java",  # JPA specific config
                    "**/database/*.{properties,yml,yaml}",  # Database properties
                    "**/jdbc/*.{properties,yml,yaml}"  # JDBC configurations
                ],
                "risk_score": 8,
                "rationale": "Database connection strings and credentials"
            },
            
            "service_integration": {
                "patterns": [
                    "**/integration/*.{properties,yml,yaml}",  # Service integration configs
                    "**/client/*.{properties,yml,yaml}",  # Client configurations
                    "**/api/*.{properties,yml,yaml}",  # API configurations
                    "**/src/**/client/RestTemplateConfig.java",  # REST client config
                    "**/src/**/client/FeignClientConfig.java",  # Feign client config
                    "**/src/**/integration/WebClientConfig.java",  # WebClient config
                    "**/src/**/config/MessageConfig.java",  # Messaging config
                    "**/src/**/integration/KafkaConfig.java",  # Kafka integration
                    "**/src/**/integration/RabbitConfig.java",  # RabbitMQ integration
                    "**/microservices/*.{properties,yml,yaml}"  # Microservice configs
                ],
                "risk_score": 7,
                "rationale": "Service-to-service communication settings"
            },

            "cloud_configurations": {
                "patterns": [
                    "**/cloud/*.{properties,yml,yaml}",  # Cloud configurations
                    "**/aws/*.{properties,yml,yaml}",  # AWS specific configs
                    "**/azure/*.{properties,yml,yaml}",  # Azure specific configs
                    "**/gcp/*.{properties,yml,yaml}",  # Google Cloud configs
                    "**/kubernetes/*.{properties,yml,yaml}",  # Kubernetes configs
                    "**/docker/*.{properties,yml,yaml}",  # Docker configurations
                    "**/consul/*.{properties,yml,yaml}",  # Consul configurations
                    "**/eureka/*.{properties,yml,yaml}",  # Eureka configurations
                    "**/src/**/cloud/CloudConfig.java",  # Cloud-specific configurations
                    "**/src/**/config/DiscoveryConfig.java"  # Service discovery configs
                ],
                "risk_score": 8,
                "rationale": "Cloud platform configurations"
            }
        }

        # Additional contexts that require examination
        self.contextual_patterns = {
            "configuration_locations": [
                "src/main/resources",
                "config",
                "src/test/resources",  # Test configs might contain real credentials
                "kubernetes",  # Kubernetes manifests
                "docker",  # Docker configurations
                "terraform",  # Infrastructure as code
                "ansible",  # Configuration management
                "deployment",  # Deployment scripts
                "scripts",  # Utility scripts
                ".github/workflows"  # CI/CD configurations
            ],
            "security_related_paths": [
                "security",
                "auth",
                "oauth2",
                "jwt",
                "crypto",
                "ssl",
                "tls",
                "certificates",
                "keys",
                "secrets",
                "tokens",
                "encryption",
                "authentication",
                "authorization",
                "identity"
            ]
        }