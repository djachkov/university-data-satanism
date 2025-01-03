const express = require("express");
const mysql = require("mysql");

const app = express();
const PORT = 3000;

// Set up EJS as the templating engine
app.set("view engine", "ejs");
app.set("views", "./templates");

// Serve static files (e.g., CSS) from the "public" directory
app.use(express.static("public"));

// MySQL Database Connection
const db = mysql.createConnection({
  host: "localhost",
  user: "root",
  password: "",
  database: "spells",
});

// Connect to MySQL
db.connect((err) => {
  if (err) {
    console.error("Error connecting to the database:", err);
    process.exit(1);
  }
  console.log("Connected to the MySQL database.");
});

// Route: Home - List all spells (Paginated)
app.get("/", (req, res) => {
  const limit = 10; // Number of spells per page
  const page = parseInt(req.query.page) || 1; // Current page, default to 1
  const offset = (page - 1) * limit;

  const { search, level, school } = req.query;

  // Base query
  let countQuery = "SELECT COUNT(*) AS total FROM spells AS s";
  let joinQuery = "JOIN schools AS sc ON s.school_id = sc.school_id";
  let spellsQuery = `
    SELECT s.spell_id, s.name, s.level, sc.school_name, s.cast_time, s.spell_range, s.duration
    FROM spells AS s
  `;
  spellsQuery += joinQuery;

  // Filters
  const filters = [];
  if (!!search) {
    filters.push(`s.name LIKE ?`);
  }
  if (!!level) {
    filters.push(`s.level = ?`);
  }
  if (!!school) {
    filters.push(`sc.school_name = ?`);
    countQuery += ` ${joinQuery}`;
  }

  if (filters.length > 0) {
    const whereClause = `WHERE ${filters.join(" AND ")}`;
    countQuery += ` ${whereClause}`;
    spellsQuery += ` ${whereClause}`;
  }

  spellsQuery += " LIMIT ? OFFSET ?";

  // Query parameters
  const params = [];
  if (search) {
    params.push(`%${search}%`);
  }
  if (level) {
    params.push(level);
  }
  if (school) {
    params.push(school);
  }
  params.push(limit, offset);

  // Fetch total count and paginated results
  db.query(countQuery, params.slice(0, -2), (err, countResults) => {
    if (err) {
      console.error("Error fetching spell count:", err);
      return res.status(500).send("Database error.");
    }

    const totalSpells = countResults[0].total;
    const totalPages = Math.ceil(totalSpells / limit);

    db.query(spellsQuery, params, (err, spellResults) => {
      if (err) {
        console.error("Error fetching spells:", err);
        return res.status(500).send("Database error.");
      }

      // Fetch unique levels and schools for filters
      const levelsQuery = "SELECT DISTINCT level FROM spells ORDER BY level";
      const schoolsQuery =
        "SELECT DISTINCT school_name FROM schools ORDER BY school_name";

      db.query(levelsQuery, (err, levels) => {
        if (err) {
          console.error("Error fetching levels:", err);
          return res.status(500).send("Database error.");
        }

        db.query(schoolsQuery, (err, schools) => {
          if (err) {
            console.error("Error fetching schools:", err);
            return res.status(500).send("Database error.");
          }

          res.render("index", {
            spells: spellResults,
            currentPage: page,
            totalPages: totalPages,
            levels: levels,
            schools: schools,
            selectedLevel: level || "",
            selectedSchool: school || "",
            search: search || "",
          });
        });
      });
    });
  });
});
// Route: Visualization Page
app.get("/visualizations", (req, res) => {
  res.render("visualizations");
});
// Route: Visualization - Spell School Distribution
app.get("/visualizations/schools", (req, res) => {
  const query = `
    SELECT sc.school_name, COUNT(*) AS count
    FROM spells AS s
    JOIN schools AS sc ON s.school_id = sc.school_id
    GROUP BY sc.school_name
  `;

  db.query(query, (err, results) => {
    if (err) {
      console.error("Error fetching school distribution:", err);
      return res.status(500).send("Database error.");
    }
    res.json(results);
  });
});

// Route: Visualization - Spell Level Distribution
app.get("/visualizations/levels", (req, res) => {
  const query = `
    SELECT level, COUNT(*) AS count
    FROM spells
    GROUP BY level
  `;

  db.query(query, (err, results) => {
    if (err) {
      console.error("Error fetching level distribution:", err);
      return res.status(500).send("Database error.");
    }
    res.json(results);
  });
});

// Route: Visualization - Spell Cast Time Distribution
app.get("/visualizations/cast-times", (req, res) => {
  const query = `
    SELECT cast_time, COUNT(*) AS count
    FROM spells
    GROUP BY cast_time
  `;

  db.query(query, (err, results) => {
    if (err) {
      console.error("Error fetching cast time distribution:", err);
      return res.status(500).send("Database error.");
    }
    res.json(results);
  });
});

// Start the server
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
