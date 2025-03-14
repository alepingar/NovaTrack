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

// @mui material components
import Card from "@mui/material/Card";
import { useEffect, useState } from "react";
// Material Dashboard 2 React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import axios from "axios";
// Billing page components
import Invoice from "layouts/billing/components/Invoice";

function Invoices() {
  const [invoices, setInvoices] = useState([]);

  useEffect(() => {
    const fetchInvoices = async () => {
      try {
        const token = localStorage.getItem("token");
        const response = await axios.get("http://127.0.0.1:8000/invoices", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        console.log(response.data);
        setInvoices(response.data);
      } catch (error) {
        console.error(error);
      }
    };
    fetchInvoices();
  }, []);

  return (
    <Card sx={{ height: "100%" }}>
      <MDBox pt={2} px={2} display="flex" justifyContent="space-between" alignItems="center">
        <MDTypography variant="h6" fontWeight="medium">
          Facturas de subscripción
        </MDTypography>
      </MDBox>
      <MDBox p={2}>
        <MDBox component="ul" display="flex" flexDirection="column" p={0} m={0}>
          {invoices && invoices.length > 0 ? (
            invoices.map((invoice, index) => (
              <Invoice
                key={index}
                date={invoice.issued_at.split("-").slice(0, 2).join("-")}
                id={invoice.id}
                price={`${invoice.amount}€`}
              />
            ))
          ) : (
            <MDTypography variant="body2" color="secondary">
              No dispone de facturas en estos momentos.
            </MDTypography>
          )}
        </MDBox>
      </MDBox>
    </Card>
  );
}

export default Invoices;
