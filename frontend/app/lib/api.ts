const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api'

interface RequestOptions extends RequestInit {
  token?: string
}

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  private async request<T>(
    endpoint: string,
    options: RequestOptions = {}
  ): Promise<T> {
    const { token, ...fetchOptions } = options

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }

    if (fetchOptions.headers) {
      Object.assign(headers, fetchOptions.headers)
    }

    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    const url = `${this.baseUrl}${endpoint}`

    try {
      const response = await fetch(url, {
        ...fetchOptions,
        headers,
      })

      if (!response.ok) {
        const error = await response.json().catch(() => ({
          message: `HTTP Error ${response.status}`,
        }))
        throw new Error(error.message || `Request failed with status ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('API request failed:', error)
      throw error
    }
  }

  // Dashboard
  async getDashboard(token?: string) {
    return this.request('/dashboard/', { token })
  }

  // Patients
  async getPatients(token?: string) {
    return this.request('/patients/', { token })
  }

  async getPatient(id: string, token?: string) {
    return this.request(`/patients/${id}/`, { token })
  }

  async createPatient(data: any, token?: string) {
    return this.request('/patients/', {
      method: 'POST',
      body: JSON.stringify(data),
      token,
    })
  }

  async updatePatient(id: string, data: any, token?: string) {
    return this.request(`/patients/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data),
      token,
    })
  }

  async deletePatient(id: string, token?: string) {
    return this.request(`/patients/${id}/`, {
      method: 'DELETE',
      token,
    })
  }

  // Appointments
  async getAppointments(token?: string) {
    return this.request('/appointments/', { token })
  }

  async getAppointment(id: string, token?: string) {
    return this.request(`/appointments/${id}/`, { token })
  }

  async createAppointment(data: any, token?: string) {
    return this.request('/appointments/', {
      method: 'POST',
      body: JSON.stringify(data),
      token,
    })
  }

  async updateAppointment(id: string, data: any, token?: string) {
    return this.request(`/appointments/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data),
      token,
    })
  }

  async deleteAppointment(id: string, token?: string) {
    return this.request(`/appointments/${id}/`, {
      method: 'DELETE',
      token,
    })
  }

  // Treatments
  async getTreatments(token?: string) {
    return this.request('/treatments/', { token })
  }

  async getTreatment(id: string, token?: string) {
    return this.request(`/treatments/${id}/`, { token })
  }

  async createTreatment(data: any, token?: string) {
    return this.request('/treatments/', {
      method: 'POST',
      body: JSON.stringify(data),
      token,
    })
  }

  async updateTreatment(id: string, data: any, token?: string) {
    return this.request(`/treatments/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data),
      token,
    })
  }

  // Payments
  async getPayments(token?: string) {
    return this.request('/payments/', { token })
  }

  async createPayment(data: any, token?: string) {
    return this.request('/payments/', {
      method: 'POST',
      body: JSON.stringify(data),
      token,
    })
  }

  // Finance
  async getFinancialSummary(token?: string) {
    return this.request('/finance/summary/', { token })
  }
}

export const apiClient = new ApiClient(API_BASE_URL)
export default apiClient
