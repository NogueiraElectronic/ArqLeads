import ChatWidget from './components/ChatWidget.tsx'

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Estudio de Arquitectura
            <span className="block text-blue-600 mt-2">Tu Visión, Nuestro Diseño</span>
          </h1>
          <p className="text-xl text-gray-700 mb-8">
            Transformamos tus ideas en espacios únicos. Especialistas en viviendas unifamiliares y reformas integrales.
          </p>
          
          <div className="bg-white rounded-lg shadow-xl p-8 mb-12">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">
              ¿Tienes un proyecto en mente?
            </h2>
            <p className="text-gray-600 mb-6">
              Habla con nuestro asistente virtual y cuéntanos tu idea. 
              Te ayudaremos a dar el primer paso.
            </p>
            <div className="flex justify-center gap-8 text-left">
              <div className="flex-1 max-w-xs">
                <div className="bg-blue-50 rounded-lg p-4">
                  <h3 className="font-semibold text-blue-900 mb-2">✨ Asesoramiento Inicial</h3>
                  <p className="text-sm text-blue-800">
                    Respuestas rápidas sobre tu proyecto
                  </p>
                </div>
              </div>
              <div className="flex-1 max-w-xs">
                <div className="bg-indigo-50 rounded-lg p-4">
                  <h3 className="font-semibold text-indigo-900 mb-2">📋 Sin Compromiso</h3>
                  <p className="text-sm text-indigo-800">
                    Información sin obligación de contratar
                  </p>
                </div>
              </div>
              <div className="flex-1 max-w-xs">
                <div className="bg-purple-50 rounded-lg p-4">
                  <h3 className="font-semibold text-purple-900 mb-2">⚡ Respuesta Inmediata</h3>
                  <p className="text-sm text-purple-800">
                    Contacto directo con un arquitecto
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Services */}
          <div className="grid md:grid-cols-3 gap-6 mb-12">
            <div className="bg-white rounded-lg p-6 shadow-md">
              <div className="text-4xl mb-4">🏠</div>
              <h3 className="text-xl font-semibold mb-2">Viviendas Unifamiliares</h3>
              <p className="text-gray-600">Diseño personalizado de tu casa ideal</p>
            </div>
            <div className="bg-white rounded-lg p-6 shadow-md">
              <div className="text-4xl mb-4">🔨</div>
              <h3 className="text-xl font-semibold mb-2">Reformas Integrales</h3>
              <p className="text-gray-600">Renovación completa de espacios</p>
            </div>
            <div className="bg-white rounded-lg p-6 shadow-md">
              <div className="text-4xl mb-4">📐</div>
              <h3 className="text-xl font-semibold mb-2">Proyectos Comerciales</h3>
              <p className="text-gray-600">Locales y oficinas a medida</p>
            </div>
          </div>

          {/* CTA */}
          <div className="bg-blue-600 text-white rounded-lg p-8 shadow-xl">
            <h2 className="text-3xl font-bold mb-4">¿Listo para empezar?</h2>
            <p className="text-xl mb-6">
              Haz clic en el botón azul de la esquina inferior derecha y cuéntanos tu proyecto 💬
            </p>
            <div className="text-sm opacity-90">
              <p>📍 Vigo, Galicia</p>
              <p>📧 contacto@estudio.com</p>
              <p>📞 +34 600 000 000</p>
            </div>
          </div>
        </div>
      </div>

      {/* Chat Widget */}
      <ChatWidget />
    </div>
  )
}

export default App