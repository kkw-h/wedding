import { PropsWithChildren } from 'react'
import { Provider } from 'react-redux'
import { configureStore } from '@reduxjs/toolkit'
import appReducer from '../store/appSlice'

const store = configureStore({ reducer: { app: appReducer } })

function StoreProvider({ children }: PropsWithChildren) {
  return <Provider store={store}>{children}</Provider>
}

export default StoreProvider
export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch