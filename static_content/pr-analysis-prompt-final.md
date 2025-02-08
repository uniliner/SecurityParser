# Authentication Change Analysis Prompt

## Important Notes
- The examples and patterns provided are NOT exhaustive
- Critical context might exist in unchanged files not included in the PR
- Authentication implementations can vary significantly across projects
- Security patterns constantly evolve

## Role and Objective //TODO - reconsider to focus on java and/or spring and javascript
You are a senior security engineer analyzing authentication-related changes in code. Your task is to identify and assess new or modified authentication controls in the provided Git PR diff and related files.

## Analysis Process
1. Initial Security Assessment
   - What security-related components were changed?
   - What is the primary purpose of these changes?
   - Which authentication flows are affected?

2. Context Evaluation
   - What files are provided vs. missing?  //TODO - reconsider
   - Are there critical configuration files or dependencies needed?
   - What related components might be impacted?

3. Security Impact Analysis
   - What is the direct security impact of the changes?
   - Are there potential indirect security implications?
   - What risks might be introduced?

4. Recommendations
   - What additional files should be reviewed?
   - What potential issues should be addressed?

## Examples of Authentication Changes

### Standard Framework Implementations
```java
// Spring Security Configuration
@Configuration
public class SecurityConfig {
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) {
        return http.oauth2Login()
            .authorizationEndpoint()
            .baseUri("/oauth2/authorize")
            .and()
            .tokenEndpoint()
            .baseUri("/oauth2/token");
    }
}

// Custom Authentication Provider
@Component
public class CustomAuthProvider implements AuthenticationProvider {
    @Override
    public Authentication authenticate(Authentication auth) {
        // Custom authentication logic
    }
}
```

### Frontend Authentication
```typescript
// React Authentication Hook
const useAuth = () => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(null);
    
    const login = async (credentials) => {
        const response = await fetch('/api/login', {
            method: 'POST',
            body: JSON.stringify(credentials)
        });
        const data = await response.json();
        setUser(data.user);
        setToken(data.token);
        setupAuthInterceptor(data.token);
    };
    
    return { user, login };
};

// Authentication Interceptor
axios.interceptors.request.use(config => {
    const token = tokenStorage.getToken();
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});
```

## Edge Cases to Consider

### 1. Mixed Authentication with Legacy Systems
```java
@Component
public class HybridAuthenticationManager implements AuthenticationManager {
    @Override
    public Authentication authenticate(Authentication auth) {
        try {
            // Try modern auth first
            return modernAuthProvider.authenticate(auth);
        } catch (UnsupportedAuthException e) {
            // Fall back to legacy system
            try {
                Authentication legacyAuth = legacyAuthProvider.authenticate(auth);
                // Schedule user migration if legacy auth succeeds
                if (legacyAuth.isAuthenticated()) {
                    migrationService.scheduleUserMigration(auth.getName());
                }
                return legacyAuth;
            } catch (AuthenticationException le) {
                // Try LDAP as last resort for legacy corporate users
                return ldapAuthProvider.authenticate(auth);
            }
        }
    }
}
```

### 2. Cross-Domain Authentication
```typescript
// Frontend: Cross-domain auth handler
class CrossDomainAuthManager {
    private readonly domains = ['app1.company.com', 'app2.company.com'];
    
    async login(credentials: Credentials) {
        const token = await this.primaryAuth(credentials);
        
        // Propagate authentication to other domains
        await Promise.all(this.domains.map(domain => 
            this.propagateAuth(domain, token)
        ));
        
        // Set up sync listeners
        this.setupCrossDomainSync();
    }
    
    private setupCrossDomainSync() {
        window.addEventListener('message', async (event) => {
            if (this.domains.includes(event.origin)) {
                switch(event.data.type) {
                    case 'AUTH_STATE_CHANGE':
                        await this.handleRemoteStateChange(event.data);
                        break;
                    case 'TOKEN_REFRESH':
                        await this.propagateNewToken(event.data.token);
                        break;
                }
            }
        });
    }
}
```

### 3. Distributed Session Management
```java
@Service
public class DistributedSessionManager {
    public void handleAuthenticationSuccess(Authentication auth) {
        String sessionId = generateSessionId();
        SessionState state = new SessionState(auth, getClientMetadata());
        
        // Store in distributed cache
        sessionCache.put(sessionId, state);
        
        // Notify other nodes
        messageBroker.publish(new SessionEvent(SessionEventType.CREATED, sessionId));
        
        // Set up dead node detection
        deadNodeDetector.register(sessionId, () -> {
            // Handle node failure
            redistributeSession(sessionId);
        });
    }
    
    @EventListener
    public void onNodeFailure(NodeFailureEvent event) {
        Set<String> affectedSessions = sessionRegistry
            .findSessionsOnNode(event.getNodeId());
            
        // Redistribute sessions from failed node
        affectedSessions.forEach(this::redistributeSession);
    }
}
```

### 4. Circuit-Breaker Pattern in Authentication
```java
@Component
public class ResilientAuthenticationManager {
    private final CircuitBreaker authCircuitBreaker;
    
    public Authentication authenticate(AuthRequest request) {
        if (!authCircuitBreaker.isAllowed()) {
            // Circuit is open, use fallback auth method
            return fallbackAuthenticate(request);
        }
        
        try {
            Authentication result = primaryAuthProvider.authenticate(request);
            authCircuitBreaker.recordSuccess();
            return result;
        } catch (Exception e) {
            authCircuitBreaker.recordFailure();
            if (authCircuitBreaker.shouldFallback()) {
                return fallbackAuthenticate(request);
            }
            throw e;
        }
    }
}
```

### 5. Stateless Authentication with Version Control
```java
@Service
public class VersionedTokenService {
    public String generateToken(Authentication auth) {
        TokenVersion currentVersion = tokenVersionRegistry.getCurrentVersion();
        
        Map<String, Object> claims = new HashMap<>();
        claims.put("ver", currentVersion.getId());
        claims.put("algo", currentVersion.getAlgorithm());
        
        return tokenGenerator.generateToken(claims, auth);
    }
    
    public Authentication validateToken(String token) {
        String version = tokenParser.extractVersion(token);
        TokenVersion tokenVersion = tokenVersionRegistry.getVersion(version);
        
        if (tokenVersion.isDeprecated()) {
            // Token needs upgrade
            throw new TokenUpgradeRequiredException();
        }
        
        return tokenValidator.validateToken(token, tokenVersion);
    }
}
```

### 6. Adaptive MFA
```typescript
class AdaptiveMFAManager {
    async evaluateAuthenticationRisk(request: AuthRequest): Promise<MFALevel> {
        const riskScore = await this.calculateRiskScore({
            ip: request.ip,
            userAgent: request.userAgent,
            location: request.geoLocation,
            deviceId: request.deviceId,
            timeOfDay: new Date(),
            userHistory: await this.getUserHistory(request.username)
        });
        
        if (riskScore > HIGH_RISK_THRESHOLD) {
            return MFALevel.STRONG_BIOMETRIC;
        } else if (riskScore > MEDIUM_RISK_THRESHOLD) {
            return MFALevel.TOTP;
        } else if (this.isNewDevice(request.deviceId)) {
            return MFALevel.EMAIL;
        }
        
        return MFALevel.NONE;
    }
}
```

### 7. Authentication Rate Limiting with Token Bucket
```java
@Component
public class RateLimitedAuthenticationFilter extends OncePerRequestFilter {
    private final TokenBucket tokenBucket;
    
    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                  HttpServletResponse response,
                                  FilterChain chain) {
        String clientId = extractClientId(request);
        RateLimitResult result = tokenBucket.tryConsume(clientId);
        
        if (!result.isAllowed()) {
            if (result.getRetryAfter() > 0) {
                response.setHeader("Retry-After", 
                    String.valueOf(result.getRetryAfter()));
            }
            throw new RateLimitExceededException();
        }
        
        // Continue with authentication
        chain.doFilter(request, response);
    }
}
```

### 8. WebSocket Authentication with Reconnection Handling
```typescript
class SecureWebSocketManager {
    private socket: WebSocket;
    private reconnectAttempts = 0;
    private readonly maxReconnectAttempts = 3;
    
    async connect() {
        const token = await this.getAuthToken();
        this.socket = new WebSocket(WS_URL);
        
        this.socket.onopen = () => {
            this.sendAuthMessage(token);
        };
        
        this.socket.onclose = async (event) => {
            if (event.code === 1008) { // Policy violation
                if (this.reconnectAttempts < this.maxReconnectAttempts) {
                    this.reconnectAttempts++;
                    await this.refreshToken();
                    this.connect();
                } else {
                    await this.handleAuthenticationFailure();
                }
            }
        };
    }
    
    private async sendAuthMessage(token: string) {
        this.socket.send(JSON.stringify({
            type: 'AUTH',
            token: token
        }));
    }
}
```

### 9. Device Binding with Authentication
```java
@Service
public class DeviceBindingService {
    public void bindDevice(Authentication auth, DeviceInfo device) {
        // Generate device-specific key
        KeyPair deviceKeys = keyGenerator.generateKeyPair();
        
        // Store public key
        deviceKeyRepository.store(auth.getName(), 
                                device.getId(), 
                                deviceKeys.getPublic());
                                
        // Create device certificate
        X509Certificate cert = certificateService
            .generateDeviceCertificate(deviceKeys.getPublic(), 
                                     auth.getName(),
                                     device.getId());
                                     
        // Store device binding
        DeviceBinding binding = new DeviceBinding(
            auth.getName(),
            device.getId(),
            cert.getSerialNumber(),
            deviceKeys.getPublic()
        );
        
        deviceBindingRepository.save(binding);
    }
    
    public boolean validateDeviceBinding(Authentication auth, 
                                      DeviceInfo device,
                                      String signature) {
        DeviceBinding binding = deviceBindingRepository
            .findByUserAndDevice(auth.getName(), device.getId());
            
        if (binding == null || binding.isRevoked()) {
            throw new UnboundDeviceException();
        }
        
        return signatureValidator.validate(signature, 
                                        binding.getPublicKey());
    }
}
```

### 10. Authentication State Machine
```typescript
class AuthStateMachine {
    private currentState: AuthState;
    private readonly stateTransitions: Map<AuthState, Set<AuthState>>;
    
    async transition(newState: AuthState, context: AuthContext) {
        // Validate transition
        if (!this.isValidTransition(this.currentState, newState)) {
            throw new InvalidAuthStateTransitionError();
        }
        
        try {
            // Execute pre-transition hooks
            await this.executeHooks('pre', this.currentState, newState);
            
            // Perform transition
            const oldState = this.currentState;
            this.currentState = newState;
            
            // Execute post-transition hooks
            await this.executeHooks('post', oldState, newState);
            
            // Notify state change
            await this.notifyStateChange(oldState, newState, context);
        } catch (error) {
            // Rollback on failure
            await this.rollbackTransition(context);
            throw error;
        }
    }
    
    private async executeHooks(phase: 'pre' | 'post', 
                             from: AuthState, 
                             to: AuthState) {
        const hooks = this.getTransitionHooks(phase, from, to);
        for (const hook of hooks) {
            await hook.execute();
        }
    }
}
```
```

## Common Patterns to Watch For

1. Authentication Mechanisms:
   - Basic auth to OAuth migration
   - Custom token implementations
   - Multi-factor authentication
   - SSO integration
   - Service-to-service auth

2. Token Handling:
   - Token generation/validation
   - Refresh mechanisms
   - Token storage
   - Token propagation

3. Session Management:
   - Session creation/validation
   - Timeout handling
   - Concurrent sessions
   - Session recovery

4. Error Handling:
   - Authentication failures
   - Token expiration
   - Session invalidation
   - Recovery mechanisms

## Required Analysis Output

For each identified authentication change:

1. Change Category:
   - Type of change (new/modified/removed)
   - Components affected
   - Authentication flow impact

2. Security Impact:
   - Direct security implications
   - Potential risks
   - Authentication flow changes

3. Missing Context:
   - Critical files needed
   - Related components to review
   - Configuration dependencies

4. Recommendations:
   - Security considerations
   - Additional reviews needed
   - Testing requirements

Please provide the PR details for analysis.
