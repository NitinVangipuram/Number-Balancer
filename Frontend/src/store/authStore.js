import { defineStore } from "pinia";
import { getAuth, onAuthStateChanged, signInWithEmailAndPassword, signOut } from "firebase/auth";
import { getFirestore, doc, getDoc } from "firebase/firestore";
import firebase from "@/firebase";

const auth = getAuth();
const db = getFirestore();

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null,
    role: null,
    isLoading: true,
  }),

  actions: {
    async fetchUser() {
        this.isLoading = true;
        
        return new Promise((resolve, reject) => {
          onAuthStateChanged(auth, async (user) => {
            if (user) {
              this.user = user;
      
              // Always fetch latest role from Firestore
              const userDoc = await getDoc(doc(db, "users", user.uid));
              if (userDoc.exists()) {
                this.role = userDoc.data().role; // ✅ Fetch the latest role
                console.log("Fetched Role:", this.role); // Debugging Output
              } else {
                this.role = "user";
              }
            } else {
              this.user = null;
              this.role = null;
            }
            this.isLoading = false;
            resolve();
          }, reject);
        });
      },      

    async login(email, password) {
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      this.user = userCredential.user;

      // Fetch user role from Firestore
      const userDoc = await getDoc(doc(db, "users", this.user.uid));
      this.role = userDoc.exists() ? userDoc.data().role : "user";

      await this.fetchUser()
    },

    async logout() {
      await signOut(auth);
      this.user = null;
      this.role = null;
    },
  },
});
