import { Button } from "@mui/material";
import { useState } from "react";
import PropTypes from "prop-types";
import dayjs from "dayjs";

function FilterButtons({ onFilterChange }) {
  const handleLast3Months = () => {
    const endDate = dayjs();
    const startDate = endDate.subtract(2, "month").startOf("month");
    onFilterChange(startDate.toDate(), endDate.toDate());
  };

  const handleLastMonth = () => {
    const endDate = dayjs().subtract(1, "month").endOf("month");
    const startDate = dayjs().subtract(1, "month").startOf("month");
    onFilterChange(startDate.toDate(), endDate.toDate());
  };

  const handleLastYear = () => {
    const endDate = dayjs().subtract(1, "year").endOf("year");
    const startDate = dayjs().subtract(1, "year").startOf("year");
    onFilterChange(startDate.toDate(), endDate.toDate());
  };

  const handlePreviousYear = () => {
    const endDate = dayjs().subtract(2, "year").endOf("year");
    const startDate = dayjs().subtract(2, "year").startOf("year");
    onFilterChange(startDate.toDate(), endDate.toDate());
  };

  return (
    <div>
      <Button onClick={handleLast3Months}>Últimos 3 meses</Button>
      <Button onClick={handleLastMonth}>Último mes</Button>
      <Button onClick={handleLastYear}>Último año</Button>
      <Button onClick={handlePreviousYear}>Año pasado</Button>
    </div>
  );
}

FilterButtons.propTypes = {
  onFilterChange: PropTypes.func.isRequired,
};

export default FilterButtons;
