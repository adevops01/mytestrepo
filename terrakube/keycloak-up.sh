docker run -p 8080:8080 --name keycloak -d \
  -e KEYCLOAK_ADMIN=admin -e KEYCLOAK_ADMIN_PASSWORD=admin \
  quay.io/keycloak/keycloak:18.0.0 start-dev



client_id='secret-client'
client_secret="LcnthKkcOqxyPFnPmgIhZjphSMYYrWsg"

redirect_uri="https://terrakube-api.minikube.net/dex/callback"

issuer_url="http://localhost:8080/realms/mjtech"
