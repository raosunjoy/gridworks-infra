import 'next-auth';
import { Permission, UserRole } from './index';

declare module 'next-auth' {
  interface Session {
    user: {
      id: string;
      name?: string | null;
      email?: string | null;
      image?: string | null;
      role?: UserRole;
      partnerId?: string;
      permissions?: Permission[];
    };
    accessToken?: string;
  }

  interface User {
    id: string;
    name?: string | null;
    email?: string | null;
    image?: string | null;
    role?: UserRole;
    partnerId?: string;
    permissions?: Permission[];
  }
}

declare module 'next-auth/jwt' {
  interface JWT {
    role?: UserRole;
    partnerId?: string;
    permissions?: Permission[];
    accessToken?: string;
  }
}