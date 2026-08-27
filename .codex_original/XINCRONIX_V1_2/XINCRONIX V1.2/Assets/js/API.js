/**
 * Cliente AJAX para llamadas a API
 * Uso: API.get('/api/usuarios').then(data => console.log(data))
 */

class API {
    static async get(endpoint) {
        return this.request('GET', endpoint);
    }
    
    static async post(endpoint, data) {
        return this.request('POST', endpoint, data);
    }
    
    static async put(endpoint, data) {
        return this.request('PUT', endpoint, data);
    }
    
    static async delete(endpoint) {
        return this.request('DELETE', endpoint);
    }
    
    static async request(method, endpoint, data = null) {
        UI.showLoading();
        
        try {
            const options = {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            };
            
            // Agregar CSRF token si existe
            const csrfInput = document.querySelector('input[name="csrf_token"]');
            if (csrfInput) {
                options.headers['X-CSRF-Token'] = csrfInput.value;
            }
            
            if (data) {
                options.body = JSON.stringify(data);
            }
            
            const response = await fetch(endpoint, options);
            const result = await response.json();
            
            UI.hideLoading();
            
            if (!result.success) {
                UI.showError(result.message);
                return null;
            }
            
            return result.data;
            
        } catch (error) {
            UI.hideLoading();
            UI.showError('Error en la solicitud: ' + error.message);
            console.error('API Error:', error);
            return null;
        }
    }
}

/**
 * Utilidades de interfaz de usuario
 */
class UI {
    static showSuccess(message) {
        this.showToast(message, 'success');
    }
    
    static showError(message) {
        this.showToast(message, 'error');
    }
    
    static showInfo(message) {
        this.showToast(message, 'info');
    }
    
    static showToast(message, type = 'info') {
        // Remover toast anterior si existe
        const existing = document.querySelector('.toast');
        if (existing) existing.remove();
        
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <span>${message}</span>
                <button class="toast-close" onclick="this.parentElement.parentElement.remove()">✕</button>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Auto remover después de 4 segundos
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 4000);
    }
    
    static showLoading() {
        let loading = document.getElementById('loading-spinner');
        if (!loading) {
            loading = document.createElement('div');
            loading.id = 'loading-spinner';
            loading.className = 'loading-spinner';
            loading.innerHTML = '<div class="spinner"></div>';
            document.body.appendChild(loading);
        }
        loading.style.display = 'flex';
    }
    
    static hideLoading() {
        const loading = document.getElementById('loading-spinner');
        if (loading) {
            loading.style.display = 'none';
        }
    }
    
    static confirm(message, callback) {
        const confirmed = window.confirm(message);
        if (confirmed && typeof callback === 'function') {
            callback();
        }
        return confirmed;
    }
}
