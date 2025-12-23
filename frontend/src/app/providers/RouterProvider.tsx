import { BrowserRouter } from "react-router-dom";
import { AppRouter } from "../../routes/AppRouter";

export function RouterProvider() {
  return (
    <BrowserRouter>
      <AppRouter />
    </BrowserRouter>
  );
}
