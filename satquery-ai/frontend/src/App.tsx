import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Workspace from './pages/Workspace'
import BenchmarkLab from './pages/BenchmarkLab'
import ModelAdaptation from './pages/ModelAdaptation'
import JudgeDemo from './pages/JudgeDemo'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Workspace />} />
        <Route path="/benchmark" element={<BenchmarkLab />} />
        <Route path="/training" element={<ModelAdaptation />} />
        <Route path="/demo" element={<JudgeDemo />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
