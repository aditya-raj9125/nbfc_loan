import NextAuth, { NextAuthOptions } from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";

// Pre-seeded Demo Personas matching the backend synthetic CRM database
const DEMO_PERSONAS = [
  {
    id: "cust_001",
    name: "Rahul Sharma",
    email: "rahul.sharma@email.com",
    role: "Instant Pre-Approved Loan",
    score: 782,
    limit: 500000,
  },
  {
    id: "cust_002",
    name: "Priya Patel",
    email: "priya.patel@email.com",
    role: "Income Verification / Salary Slip",
    score: 820,
    limit: 750000,
  },
  {
    id: "cust_005",
    name: "Vikram Singh",
    email: "vikram.singh@email.com",
    role: "Credit Score < 700 (Rejection Demo)",
    score: 680,
    limit: 400000,
  },
  {
    id: "cust_006",
    name: "Anjali Verma",
    email: "anjali.verma@email.com",
    role: "KYC Verification Flow",
    score: 730,
    limit: 250000,
  },
  {
    id: "cust_007",
    name: "Rajesh Gupta",
    email: "rajesh.gupta@email.com",
    role: "High Value Pre-Approved (10 Lakhs)",
    score: 800,
    limit: 1000000,
  },
  {
    id: "cust_003",
    name: "Amit Kumar",
    email: "amit.kumar@email.com",
    role: "Standard Applicant",
    score: 715,
    limit: 300000,
  },
  {
    id: "cust_004",
    name: "Sneha Reddy",
    email: "sneha.reddy@email.com",
    role: "Standard Applicant",
    score: 750,
    limit: 600000,
  },
  {
    id: "cust_008",
    name: "Meera Nair",
    email: "meera.nair@email.com",
    role: "Standard Applicant",
    score: 740,
    limit: 450000,
  },
  {
    id: "cust_009",
    name: "Arjun Malhotra",
    email: "arjun.malhotra@email.com",
    role: "Credit Score < 700 (Rejection Demo)",
    score: 660,
    limit: 350000,
  },
  {
    id: "cust_010",
    name: "Divya Iyer",
    email: "divya.iyer@email.com",
    role: "Fast Track Approval",
    score: 790,
    limit: 700000,
  },
];

const authOptions: NextAuthOptions = {
  providers: [
    CredentialsProvider({
      name: "Demo Credentials",
      credentials: {
        email: { label: "Email", type: "email", placeholder: "rahul.sharma@email.com" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        if (!credentials?.email) {
          return null;
        }

        const inputEmail = credentials.email.toLowerCase().trim();

        // 1. Guest Login support
        if (inputEmail === "guest" || inputEmail === "guest@temp.local") {
          return {
            id: "guest",
            name: "Guest Applicant",
            email: "guest@temp.local",
          };
        }

        // 2. Check pre-seeded test personas
        const persona = DEMO_PERSONAS.find(
          (p) => p.email.toLowerCase() === inputEmail
        );

        if (persona) {
          return {
            id: persona.id,
            name: persona.name,
            email: persona.email,
          };
        }

        // 3. Fallback: Accept any valid-looking email for testing flexibility
        const nameFromEmail = inputEmail.split("@")[0].replace(/[._]/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
        return {
          id: `custom_${Date.now()}`,
          name: nameFromEmail || "Test User",
          email: inputEmail,
        };
      },
    }),
  ],
  callbacks: {
    async session({ session, token }) {
      if (session.user) {
        session.user.id = (token.sub as string) || (token.id as string) || "";
      }
      return session;
    },
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id;
      }
      return token;
    },
  },
  pages: {
    signIn: "/login",
  },
  session: {
    strategy: "jwt",
    maxAge: 30 * 24 * 60 * 60, // 30 days
  },
  secret: process.env.NEXTAUTH_SECRET || "nbfc-loan-chatbot-super-secret-key-2025",
};

const handler = NextAuth(authOptions);

export { handler as GET, handler as POST };
