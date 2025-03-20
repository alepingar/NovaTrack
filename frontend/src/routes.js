/**
=========================================================
* Material Dashboard 2 React - v2.2.0
=========================================================

* Product Page: https://www.creative-tim.com/product/material-dashboard-react
* Copyright 2023 Creative Tim (https://www.creative-tim.com)

Coded by www.creative-tim.com

 =========================================================

* The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
*/

/** 
  All of the routes for the Material Dashboard 2 React are added here,
  You can add a new route, customize the routes and delete the routes here.

  Once you add a new route on this file it will be visible automatically on
  the Sidenav.

  For adding a new route you can follow the existing routes in the routes array.
  1. The `type` key with the `collapse` value is used for a route.
  2. The `type` key with the `title` value is used for a title inside the Sidenav. 
  3. The `type` key with the `divider` value is used for a divider between Sidenav items.
  4. The `name` key is used for the name of the route on the Sidenav.
  5. The `key` key is used for the key of the route (It will help you with the key prop inside a loop).
  6. The `icon` key is used for the icon of the route on the Sidenav, you have to add a node.
  7. The `collapse` key is used for making a collapsible item on the Sidenav that has other routes
  inside (nested routes), you need to pass the nested routes inside an array as a value for the `collapse` key.
  8. The `route` key is used to store the route location which is used for the react router.
  9. The `href` key is used to store the external links location.
  10. The `title` key is only for the item with the type of `title` and its used for the title text on the Sidenav.
  10. The `component` key is used to store the component of its route.
*/

// Material Dashboard 2 React layouts
import Dashboard from "layouts/dashboard";
import Tables from "layouts/tables";
import Billing from "layouts/billing";
import Notifications from "layouts/notifications";
import Profile from "layouts/profile";
import SignIn from "layouts/authentication/sign-in";
import SignUp from "layouts/authentication/sign-up";
import Logout from "layouts/authentication/log-out";
import TransferDetails from "layouts/tables/data/transfersDetails";
import GeneralDashboard from "layouts/dashboard/generalDashboard";
import ForgotPassword from "layouts/authentication/forgot-password";
import ResetPassword from "layouts/authentication/reset-password";
import {
  TermsOfService,
  PrivacyPolicy,
  Support,
  About,
  DataProcessing,
} from "examples/Footer/legalPages";
import SubscriptionUpgrade from "layouts/suscriptions";
// @mui icons
import Icon from "@mui/material/Icon";

const routes = [
  {
    type: "collapse",
    name: "Dashboard",
    key: "dashboard",
    icon: <Icon fontSize="small">dashboard</Icon>,
    route: "/dashboard",
    component: <Dashboard />,
    protected: true,
  },
  {
    type: "collapse",
    name: "Dashboard General",
    key: "general-dashboard",
    icon: <Icon fontSize="small">general_dashboard</Icon>,
    route: "/general-dashboard",
    component: <GeneralDashboard />,
    protected: false,
    onlyGuest: true,
  },
  {
    type: "collapse",
    name: "Transferencias",
    key: "tables",
    icon: <Icon fontSize="small">table_view</Icon>,
    route: "/tables",
    component: <Tables />,
    protected: true,
  },
  {
    type: "collapse",
    name: "Facturación",
    key: "billing",
    icon: <Icon fontSize="small">receipt_long</Icon>,
    route: "/billing",
    component: <Billing />,
    protected: true,
  },
  {
    type: "collapse",
    name: "Notificaciones",
    key: "notifications",
    icon: <Icon fontSize="small">notifications</Icon>,
    route: "/notifications",
    component: <Notifications />,
    protected: true,
  },
  {
    type: "collapse",
    name: "Datos de la cuenta",
    key: "profile",
    icon: <Icon fontSize="small">person</Icon>,
    route: "/profile",
    component: <Profile />,
    protected: true,
  },
  {
    type: "invisible",
    route: "/forgot-password",
    component: <ForgotPassword />,
    protected: false,
  },
  {
    type: "invisible",
    route: "/reset-password",
    component: <ResetPassword />,
    protected: false,
  },
  {
    type: "invisible",
    route: "/transfers/:id",
    component: <TransferDetails />,
    protected: true,
  },
  {
    type: "invisible",
    route: "/subscriptions",
    component: <SubscriptionUpgrade />,
    protected: true,
  },
  {
    type: "invisible",
    name: "Términos de sérvicio",
    key: "terms_of_service",
    icon: <Icon fontSize="small">terms_of_service</Icon>,
    route: "/terms",
    component: <TermsOfService />,
    protected: false,
  },
  {
    type: "invisible",
    name: "Uso de datos",
    key: "data_processing",
    icon: <Icon fontSize="small">data_processing</Icon>,
    route: "/data_processing",
    component: <DataProcessing />,
    protected: false,
  },
  {
    type: "invisible",
    name: "Política de privacidad",
    key: "privacy_policy",
    icon: <Icon fontSize="small">privacy_policy</Icon>,
    route: "/privacy-policy",
    component: <PrivacyPolicy />,
    protected: false,
  },
  {
    type: "invisible",
    name: "Support",
    key: "support",
    icon: <Icon fontSize="small">support</Icon>,
    route: "/support",
    component: <Support />,
    protected: false,
  },
  {
    type: "invisible",
    name: "About",
    key: "about",
    icon: <Icon fontSize="small">about</Icon>,
    route: "/about",
    component: <About />,
    protected: false,
  },
  {
    type: "collapse",
    name: "Inicio de Sesión",
    key: "sign-in",
    icon: <Icon fontSize="small">login</Icon>,
    route: "/authentication/sign-in",
    component: <SignIn />,
    protected: false,
    onlyGuest: true,
  },
  {
    type: "collapse",
    name: "Registro",
    key: "sign-up",
    icon: <Icon fontSize="small">assignment</Icon>,
    route: "/authentication/sign-up",
    component: <SignUp />,
    protected: false,
    onlyGuest: true,
  },
  {
    type: "collapse",
    name: "Cerrar Sesión",
    key: "log-out",
    icon: <Icon fontSize="small">logout</Icon>,
    route: "/authentication/log-out",
    component: <Logout />,
    protected: true,
    onlyAuth: true,
  },
].filter(Boolean);

export default routes;
