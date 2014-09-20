package com.alarmez.alarmez;

import android.app.NotificationManager;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.database.Cursor;
import android.media.AudioManager;
import android.media.Ringtone;
import android.media.RingtoneManager;
import android.net.Uri;
import android.os.IBinder;
import android.support.v4.app.NotificationCompat;
import android.util.Log;
import android.widget.Toast;

public class AlarmEZService extends Service {
	
	@Override
	public void onCreate() {
		System.out.println("Service created.");
		super.onCreate();
	}
	
	@Override
	public int onStartCommand(Intent intent, int flags, int startId) {
		System.out.println("Service started.");
		super.onStartCommand(intent, flags, startId);
		
		NotificationCompat.Builder mBuilder =
                new NotificationCompat.Builder(this)
                .setSmallIcon(R.drawable.ic_launcher)
                .setContentTitle("My notification")
                .setContentText("Hello World!");
        // Creates an explicit intent for an Activity in your app
        
        NotificationManager mNotificationManager =
            (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
        // mId allows you to update the notification later on.
        int mId = 0;
        mNotificationManager.notify(mId, mBuilder.build());
		
        AudioManager audio = (AudioManager) this.getApplicationContext().getSystemService(Context.AUDIO_SERVICE);
        int currentVolume = audio.getStreamVolume(AudioManager.STREAM_RING);
        int max = audio.getStreamMaxVolume(AudioManager.STREAM_NOTIFICATION);
        //audio.setRingerMode(AudioManager.RINGER_MODE_NORMAL);
        //audio.setStreamVolume(AudioManager.STREAM_RING, max, AudioManager.FLAG_REMOVE_SOUND_AND_VIBRATE);
        
        RingtoneManager ringtoneManager = new RingtoneManager(this);
        ringtoneManager.setType(RingtoneManager.TYPE_ALARM);
        Cursor alarmCursor = ringtoneManager.getCursor();
        for(int i = 0; i < alarmCursor.getCount(); i++)
        	System.out.println(ringtoneManager.getRingtone(i).getTitle(this.getApplicationContext()));
        
        Ringtone r = ringtoneManager.getRingtone(0);
        //r.play();
        
		return START_STICKY;
	}

	@Override
	public IBinder onBind(Intent intent) {
		// TODO for communication return IBinder implementation
		return null;
	}
}