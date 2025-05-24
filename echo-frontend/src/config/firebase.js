/**
 * Firebase Configuration and Initialization
 */

import { initializeApp } from 'firebase/app'
import { 
  getAuth, 
  GoogleAuthProvider, 
  signInWithPopup,
  signOut as firebaseSignOut,
  onAuthStateChanged
} from 'firebase/auth'
import { 
  getFirestore,
  enableIndexedDbPersistence,
  collection,
  doc,
  getDoc,
  setDoc,
  updateDoc,
  query,
  where,
  orderBy,
  limit,
  onSnapshot
} from 'firebase/firestore'
import { getFunctions, httpsCallable, connectFunctionsEmulator } from 'firebase/functions'
import { getAnalytics } from 'firebase/analytics'

// Firebase configuration
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
  measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID
}

// Initialize Firebase
const app = initializeApp(firebaseConfig)

// Initialize services
export const auth = getAuth(app)
export const db = getFirestore(app)
export const functions = getFunctions(app)
export const analytics = getAnalytics(app)

// Enable offline persistence
enableIndexedDbPersistence(db).catch((err) => {
  if (err.code === 'failed-precondition') {
    console.warn('Persistence failed: Multiple tabs open')
  } else if (err.code === 'unimplemented') {
    console.warn('Persistence not available')
  }
})

// Connect to emulators in development
if (import.meta.env.DEV) {
  connectFunctionsEmulator(functions, 'localhost', 5001)
}

// Auth providers
export const googleProvider = new GoogleAuthProvider()
googleProvider.setCustomParameters({
  prompt: 'select_account'
})

// Auth functions
export const signInWithGoogle = async () => {
  try {
    const result = await signInWithPopup(auth, googleProvider)
    const user = result.user
    
    // Create/update user document
    const userRef = doc(db, 'users', user.uid)
    const userDoc = await getDoc(userRef)
    
    if (!userDoc.exists()) {
      // Create new user document
      await setDoc(userRef, {
        uid: user.uid,
        email: user.email,
        displayName: user.displayName,
        photoURL: user.photoURL,
        createdAt: new Date(),
        autonomySettings: {
          email: 2,
          slack: 1,
          sms: 0
        },
        preferences: {
          communicationStyle: 'balanced',
          responseLength: 'concise'
        }
      })
    } else {
      // Update last login
      await updateDoc(userRef, {
        lastLogin: new Date()
      })
    }
    
    return user
  } catch (error) {
    console.error('Error signing in with Google:', error)
    throw error
  }
}

export const signOut = () => firebaseSignOut(auth)

// Firestore helpers
export const getUserData = async (userId) => {
  const userRef = doc(db, 'users', userId)
  const userDoc = await getDoc(userRef)
  return userDoc.exists() ? userDoc.data() : null
}

export const updateUserAutonomy = async (userId, platform, level) => {
  const userRef = doc(db, 'users', userId)
  await updateDoc(userRef, {
    [`autonomySettings.${platform}`]: level
  })
}

export const createAgent = async (userId, agentData) => {
  const agentsRef = collection(db, 'agents')
  return await setDoc(doc(agentsRef), {
    ...agentData,
    userId,
    createdAt: new Date(),
    updatedAt: new Date()
  })
}

export const subscribeToMessages = (userId, callback, platformFilter = null) => {
  let q = query(
    collection(db, 'messages'),
    where('userId', '==', userId),
    orderBy('timestamp', 'desc'),
    limit(50)
  )
  
  if (platformFilter) {
    q = query(
      collection(db, 'messages'),
      where('userId', '==', userId),
      where('platform', '==', platformFilter),
      orderBy('timestamp', 'desc'),
      limit(50)
    )
  }
  
  return onSnapshot(q, (snapshot) => {
    const messages = []
    snapshot.forEach((doc) => {
      messages.push({ id: doc.id, ...doc.data() })
    })
    callback(messages)
  })
}

// Cloud Functions
export const processMessageFunction = httpsCallable(functions, 'processMessage')
export const submitFeedbackFunction = httpsCallable(functions, 'submitFeedback')
export const getEvolutionMetricsFunction = httpsCallable(functions, 'getEvolutionMetrics')

// Auth state observer
export const onAuthStateChange = (callback) => {
  return onAuthStateChanged(auth, callback)
}

// Export auth state helper
export const getCurrentUser = () => auth.currentUser

// Integration helpers
export const integrateGmail = async () => {
  const integrateGmailFunction = httpsCallable(functions, 'integrateGmail')
  return await integrateGmailFunction()
}

export const integrateSlack = async (workspaceCode) => {
  const integrateSlackFunction = httpsCallable(functions, 'integrateSlack')
  return await integrateSlackFunction({ code: workspaceCode })
}

export default {
  auth,
  db,
  functions,
  analytics,
  signInWithGoogle,
  signOut,
  getCurrentUser,
  onAuthStateChange
}