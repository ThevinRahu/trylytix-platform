import "@aws-amplify/ui-react/styles.css";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import RugbyEventTracker from "./events/RugbyEventTracker";
import RootLayout from "./RootLayout";

const router = createBrowserRouter([
  {
    path: "/",
    element: <RootLayout />,

    id: "root",

    children: [
      {
        path: "/",
        element: <RugbyEventTracker />,
      },
    ],
  },
]);

function App() {
  return <RouterProvider router={router} />;
}

export default App;