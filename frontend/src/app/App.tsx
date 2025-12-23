// import { useEffect } from "react";
// import { AppRouter } from "../routes/AppRouter";
// import { useAuthStore } from "../state/auth";
// import { supabase } from "../lib/supabase";

// export default function App() {
//   const setSession = useAuthStore((s) => s.setSession);

//   useEffect(() => {
//     // Hydrate session from URL hash or storage
//     supabase.auth.getSession().then(({ data }) => {
//       setSession(data.session ?? null);
//     });

//     // Listen for future auth changes
//     const {
//       data: { subscription },
//     } = supabase.auth.onAuthStateChange((_event, session) => {
//       setSession(session);
//     });

//     return () => {
//       subscription.unsubscribe();
//     };
//   }, [setSession]);

//   return <AppRouter />;
// }

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

