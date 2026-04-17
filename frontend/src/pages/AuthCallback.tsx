import { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import api from '../utils/api'
import { useAuthStore } from '../store/authStore'
import LoadingSpinner from '../components/LoadingSpinner'

export default function AuthCallback() {
  const [params] = useSearchParams()
  const navigate = useNavigate()
  const { login } = useAuthStore()

  useEffect(() => {
    const token = params.get('token')
    const error = params.get('error')

    if (error) {
      navigate(`/?error=${encodeURIComponent(error)}`)
      return
    }

    if (!token) {
      navigate('/?error=missing_token')
      return
    }

    api
      .get(`/api/auth/me?token=${token}`)
      .then(({ data }) => {
        login(data, token)
        navigate('/dashboard')
      })
      .catch(() => {
        navigate('/?error=session_validation_failed')
      })
  }, [])

  return (
    <div className="min-h-screen bg-apple-gray flex items-center justify-center flex-col gap-4">
      <LoadingSpinner size={40} />
      <p className="text-apple-darkgray text-sm">Signing you in...</p>
    </div>
  )
}
