import { createBrowserRouter } from 'react-router-dom'

import { RequireAuth } from '../components'
import { ChatPage, LoginPage, NotFoundPage } from '../pages'

export const router = createBrowserRouter([
  {
    element: <RequireAuth />,
    children: [{ path: '/', element: <ChatPage /> }],
  },
  { path: '/login', element: <LoginPage /> },
  { path: '*', element: <NotFoundPage /> },
])
