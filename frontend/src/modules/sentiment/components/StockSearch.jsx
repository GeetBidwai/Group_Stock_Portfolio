import { StockAutocomplete } from "../../portfolio/components/StockAutocomplete";

export function StockSearch({ value, onChange, onSelect }) {
  return (
    <div className="form" style={{ gap: 10 }}>
      <label className="muted" style={{ fontSize: 13 }}>Stock Search</label>
      <StockAutocomplete
        value={value}
        onChange={onChange}
        onSelect={onSelect}
        placeholder="Search any stock symbol"
        noResultsText="No matching stocks found"
      />
    </div>
  );
}

