import { ThemeProvider } from "./providers/ThemeProvider";
import { RouterProvider } from "./providers/RouterProvider";
import { AuthProvider } from "./providers/AuthProvider";

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <RouterProvider />
      </AuthProvider>
    </ThemeProvider>
  );
}
