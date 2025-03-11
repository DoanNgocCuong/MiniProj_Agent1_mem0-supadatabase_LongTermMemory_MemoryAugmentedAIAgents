import { createClient, SupabaseClient } from '@supabase/supabase-js';

// Supabase setup
const supabaseUrl = process.env.REACT_APP_SUPABASE_URL || '';
const supabaseKey = process.env.REACT_APP_SUPABASE_KEY || '';

// Create Supabase client
const supabase: SupabaseClient = createClient(supabaseUrl, supabaseKey);

export interface AuthUser {
  id: string;
  email: string;
  full_name?: string;
}

export const signUp = async (email: string, password: string, full_name: string) => {
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
    options: {
      data: {
        full_name,
      },
    },
  });

  if (error) {
    throw new Error(error.message);
  }
  
  return data;
};

export const signIn = async (email: string, password: string) => {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
  });

  if (error) {
    throw new Error(error.message);
  }
  
  return data;
};

export const signOut = async () => {
  const { error } = await supabase.auth.signOut();
  
  if (error) {
    throw new Error(error.message);
  }
  
  return true;
};

export const getCurrentUser = async (): Promise<AuthUser | null> => {
  const { data } = await supabase.auth.getUser();
  
  if (!data.user) {
    return null;
  }
  
  return {
    id: data.user.id,
    email: data.user.email || '',
    full_name: data.user.user_metadata?.full_name
  };
};

export default supabase; 