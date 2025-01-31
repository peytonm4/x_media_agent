import { useState, useEffect } from "react";
import axios from "axios";
import { Card, CardContent } from "./Card";
import { Button } from "./Button";
import { Input } from "./Input";
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from "./Select";

export default function MediaAgent() {
  const [username, setUsername] = useState("");
  const [report, setReport] = useState("");
  const [recentSearches, setRecentSearches] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchRecentSearches();
  }, []);

  const fetchRecentSearches = async () => {
    try {
      const response = await axios.get("/recent_searches/");
      setRecentSearches(response.data);
    } catch (error) {
      console.error("Error fetching recent searches", error);
    }
  };

  const generateReport = async () => {
    if (!username) {
      setError("Please enter a username");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const response = await axios.post("/generate_report/", { username });
      setReport(response.data.report);
      fetchRecentSearches(); // Refresh recent searches
    } catch (error) {
      setError(error.response?.data?.detail || "An error occurred");
    }
    setLoading(false);
  };

  return (
    <div className="max-w-xl mx-auto p-6 space-y-4">
      <h1 className="text-2xl font-bold">X Media Agent</h1>
      <div className="flex gap-2">
        <Input
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Enter username"
        />
        <Button onClick={generateReport} disabled={loading}>
          {loading ? "Generating..." : "Get Report"}
        </Button>
      </div>
      {/* {recentSearches.length > 0 && (
        <Select onValueChange={setUsername}>
          <SelectTrigger>
            <SelectValue placeholder="Recent Searches" />
          </SelectTrigger>
          <SelectContent>
            {recentSearches.map((user, index) => (
              <SelectItem key={index} value={user}>
                {user}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      )} */}
      {error && <p className="text-red-500">{error}</p>}
      {report && (
        <Card>
          <CardContent>
            <p className="whitespace-pre-line">{report}</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

