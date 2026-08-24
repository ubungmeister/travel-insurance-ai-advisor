import { createBrowserRouter } from 'react-router-dom'

import { ChatPage, NotFoundPage } from '../pages'

export const router = createBrowserRouter([
  { path: '/', element: <ChatPage /> },
  { path: '*', element: <NotFoundPage /> },
])
