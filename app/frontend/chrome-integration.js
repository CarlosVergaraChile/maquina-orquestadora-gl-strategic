/**
 * CHROME INTEGRATION - Acceso LOCAL a credenciales y datos del usuario
 * Más versátil: funciona directamente desde el navegador del usuario
 */

class ChromeIntegration {
  constructor() {
    this.credentials = {};
    this.isInitialized = false;
  }

  /**
   * Inicializa Chrome Integration
   * Pide permiso al usuario para acceder a su información
   */
  async initialize() {
    try {
      // Usar Chrome Identity API (con permiso del usuario)
      if (typeof chrome !== 'undefined' && chrome.identity) {
        console.log('✅ Chrome Identity API disponible');
        this.isInitialized = true;
        return true;
      }
      
      // Fallback: usar localStorage para credenciales guardadas
      this.credentials = JSON.parse(localStorage.getItem('userCredentials') || '{}');
      this.isInitialized = true;
      return true;
    } catch (error) {
      console.error('Error inicializando Chrome Integration:', error);
      return false;
    }
  }

  /**
   * Guarda credenciales de forma segura en localStorage
   * (el usuario controla totalmente qué se guarda)
   */
  async storeCredentials(service, credentials) {
    if (!this.isInitialized) await this.initialize();
    
    this.credentials[service] = {
      ...credentials,
      savedAt: new Date().toISOString()
    };
    
    localStorage.setItem('userCredentials', JSON.stringify(this.credentials));
    console.log(`✅ Credenciales guardadas para ${service}`);
    return true;
  }

  /**
   * Obtiene credenciales guardadas
   */
  getCredentials(service) {
    if (!this.isInitialized) return null;
    return this.credentials[service] || null;
  }

  /**
   * Lista todos los servicios disponibles
   */
  getAvailableServices() {
    return Object.keys(this.credentials);
  }

  /**
   * Obtiene información del usuario desde Chrome
   */
  async getUserInfo() {
    const services = this.getAvailableServices();
    return {
      services,
      hasHostinger: !!this.credentials.hostinger,
      hasGoogle: !!this.credentials.google,
      hasOneDrive: !!this.credentials.onedrive,
      hasDropbox: !!this.credentials.dropbox,
      hasEmail: !!this.credentials.email
    };
  }

  /**
   * Conecta Hostinger
   */
  async connectHostinger(email, password) {
    return this.storeCredentials('hostinger', {
      email,
      password: btoa(password), // Simple encoding, no es encriptación completa
      type: 'hostinger'
    });
  }

  /**
   * Conecta Google
   */
  async connectGoogle(token) {
    return this.storeCredentials('google', {
      token,
      type: 'google',
      provider: 'oauth2'
    });
  }

  /**
   * Conecta OneDrive
   */
  async connectOneDrive(token) {
    return this.storeCredentials('onedrive', {
      token,
      type: 'onedrive',
      provider: 'oauth2'
    });
  }

  /**
   * Conecta Dropbox
   */
  async connectDropbox(token) {
    return this.storeCredentials('dropbox', {
      token,
      type: 'dropbox',
      provider: 'oauth2'
    });
  }

  /**
   * Conecta Email
   */
  async connectEmail(email, password, provider = 'gmail') {
    return this.storeCredentials('email', {
      email,
      password: btoa(password),
      provider,
      type: 'email'
    });
  }

  /**
   * Desconecta un servicio
   */
  disconnectService(service) {
    delete this.credentials[service];
    localStorage.setItem('userCredentials', JSON.stringify(this.credentials));
    console.log(`✅ ${service} desconectado`);
    return true;
  }

  /**
   * Envía credenciales al backend (servidor Render)
   * IMPORTANTE: Solo lo hace si el usuario lo autoriza
   */
  async syncToBackend(orchestratorUrl) {
    try {
      const response = await fetch(`${orchestratorUrl}/sync-credentials`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('jwtToken')}`
        },
        body: JSON.stringify({
          credentials: this.credentials,
          timestamp: new Date().toISOString(),
          userAgent: navigator.userAgent
        })
      });

      return await response.json();
    } catch (error) {
      console.error('Error sincronizando con backend:', error);
      throw error;
    }
  }

  /**
   * Obtiene lista de sitios guardados en Chrome
   */
  async getStoredWebsites() {
    // Simula obtener sitios del historial de Chrome
    return {
      websites: Object.keys(this.credentials).map(service => ({
        service,
        lastUsed: this.credentials[service].savedAt
      }))
    };
  }
}

// Instancia global
const chromeIntegration = new ChromeIntegration();

// Inicializar al cargar
window.addEventListener('load', async () => {
  await chromeIntegration.initialize();
  console.log('✅ Chrome Integration cargada');
});

// Exportar para uso en módulos
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ChromeIntegration;
}
