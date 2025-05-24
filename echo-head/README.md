# 🤖 AI Head - Open Source Animated AI Avatar

A customizable, animated AI head component for web applications. Features voice synthesis, facial expressions, and real-time animations.

![License](https://img.shields.io/badge/license-MIT-green)
![Version](https://img.shields.io/badge/version-1.0.0-blue)

## ✨ Features

- 🎨 Customizable wireframe design
- 🗣️ Voice synthesis with adjustable parameters
- 🎤 Speech recognition support
- 😊 Facial expressions and animations
- 📊 Audio visualization
- 🎮 Multiple rendering modes (Canvas 2D, WebGL, ASCII)
- 🔌 Framework agnostic

## 🚀 Quick Start

### Vanilla JavaScript
```html
<div id="ai-head"></div>
<script src="https://unpkg.com/@agentic-persona/ai-head"></script>
<script>
  const head = new AIHead({
    container: '#ai-head',
    theme: 'cyberpunk',
    voice: { rate: 0.9, pitch: 1.1 }
  });
  
  head.speak("Hello, I'm your AI assistant!");
</script>
```

### Vue Component
```vue
<template>
  <AIHead 
    :theme="theme"
    :enable-voice="true"
    @speech-end="onSpeechEnd"
  />
</template>

<script>
import AIHead from '@agentic-persona/ai-head-vue'
export default {
  components: { AIHead }
}
</script>
```

### React Component
```jsx
import { AIHead } from '@agentic-persona/ai-head-react'

function App() {
  return (
    <AIHead 
      theme="matrix"
      enableVoice={true}
      onSpeechEnd={() => console.log('Done speaking')}
    />
  )
}
```

## 🎨 Themes

### Built-in Themes
- `cyberpunk` - Neon green wireframe (default)
- `matrix` - Matrix-style green on black
- `hologram` - Blue holographic effect
- `retro` - 80s synthwave style
- `minimal` - Clean, simple lines

### Custom Theme
```javascript
const head = new AIHead({
  theme: {
    primary: '#ff0080',
    secondary: '#0080ff',
    background: '#000033',
    glow: true,
    glowIntensity: 20
  }
})
```

## 🎭 Expressions

```javascript
// Trigger expressions
head.setExpression('happy')
head.setExpression('thinking')
head.setExpression('surprised')
head.setExpression('neutral')

// Custom expression
head.setExpression({
  mouth: { openness: 0.8, curve: 0.5 },
  eyes: { openness: 1.2, position: { x: 0, y: -5 } },
  eyebrows: { height: 10, angle: 15 }
})
```

## 🎤 Voice Features

```javascript
// Text to speech
head.speak("Hello world!", {
  rate: 1.0,      // Speed (0.1 - 10)
  pitch: 1.0,     // Pitch (0 - 2)
  volume: 1.0,    // Volume (0 - 1)
  voice: 'en-US'  // Language/voice
})

// Speech recognition
head.startListening({
  continuous: true,
  onResult: (transcript) => {
    console.log('User said:', transcript)
  }
})
```

## ⚙️ Configuration

```javascript
const config = {
  // Container
  container: '#ai-head',
  width: 400,
  height: 400,
  
  // Rendering
  renderer: 'canvas2d', // 'canvas2d', 'webgl', 'ascii'
  fps: 60,
  
  // Appearance
  theme: 'cyberpunk',
  showSkull: true,
  showJaw: true,
  showNeck: false,
  
  // Animation
  idleAnimation: true,
  blinkInterval: 4000,
  breathingEffect: true,
  
  // Audio
  enableVoice: true,
  enableListening: true,
  visualizeAudio: true,
  
  // Interaction
  interactive: true,
  followMouse: false,
  respondToSound: true
}
```

## 🔧 API Reference

### Methods
- `speak(text, options)` - Make the head speak
- `stopSpeaking()` - Stop current speech
- `startListening(options)` - Start speech recognition
- `stopListening()` - Stop speech recognition
- `setExpression(expression)` - Change facial expression
- `animate(animation)` - Play animation
- `setTheme(theme)` - Change theme
- `destroy()` - Clean up resources

### Events
- `speaking` - Speech started
- `speechEnd` - Speech finished
- `listening` - Started listening
- `transcript` - Speech recognized
- `expressionChange` - Expression changed
- `error` - Error occurred

## 🎮 Advanced Features

### 3D Mode (WebGL)
```javascript
const head = new AIHead({
  renderer: 'webgl',
  depth: true,
  rotation: { x: 0, y: 0, z: 0 },
  lighting: {
    ambient: 0.4,
    directional: 0.6
  }
})
```

### ASCII Mode
```javascript
const head = new AIHead({
  renderer: 'ascii',
  asciiChars: ' .:-=+*#%@',
  fontSize: 8
})
```

### Custom Animations
```javascript
head.addAnimation('nod', [
  { rotation: { x: 0 }, duration: 200 },
  { rotation: { x: 10 }, duration: 200 },
  { rotation: { x: -10 }, duration: 200 },
  { rotation: { x: 0 }, duration: 200 }
])

head.playAnimation('nod')
```

## 📦 Installation

### NPM
```bash
npm install @agentic-persona/ai-head
```

### CDN
```html
<script src="https://unpkg.com/@agentic-persona/ai-head"></script>
```

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md)

## 📄 License

MIT License - see [LICENSE](LICENSE)

## 🔗 Links

- [Demo](https://ai-head-demo.netlify.app)
- [Documentation](https://docs.agentic-persona.dev/ai-head)
- [GitHub](https://github.com/agentic-persona/ai-head)