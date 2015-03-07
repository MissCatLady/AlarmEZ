package com.alarmez.alarmez;

import android.app.Activity;
import android.app.AlertDialog;
import android.app.Fragment;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.ServiceConnection;
import android.database.Cursor;
import android.media.RingtoneManager;
import android.os.Bundle;
import android.os.IBinder;
import android.preference.PreferenceActivity;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.Toast;
import android.content.ComponentName;


public class MainActivity extends Activity{

    //Handle to AlarmEZService
    private AlarmEZService mBoundService;

    //Connection establisher to AlarmEZService.
    ServiceConnection mConnection = new ServiceConnection(){
        public void onServiceConnected(ComponentName className, IBinder service) {
            mBoundService = ((AlarmEZService.AlarmEZBinder)service).getService();

            //Stop alarm, temporarily here.
            mBoundService.stopAlarm();

            Toast.makeText(getApplicationContext(), "Service connected", Toast.LENGTH_SHORT).show();
        }

        public void onServiceDisconnected(ComponentName className) {
            mBoundService = null;

            Toast.makeText(getApplicationContext(), "Service Disconnected", Toast.LENGTH_SHORT).show();
        }
    };

	Fragment currentFragment = null;
	
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        ComponentName service = startService(new Intent(getBaseContext(), AlarmEZService.class));

        //Open connection the AlarmEZService.
        bindService(new Intent(this, AlarmEZService.class), mConnection, Context.BIND_AUTO_CREATE);

        //Get calling intent
        //TODO: If notification click, disable alarms.
        System.out.println("onCreate");
        Intent callingIntent = getIntent();
        if(callingIntent != null){
            System.out.println("Created from notification.");
            System.out.println(callingIntent.getDataString());
        }
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();
        if (id == R.id.action_settings) {
        	currentFragment = new SettingsFragment();
        	// Display the fragment as the main content.
            getFragmentManager().beginTransaction()
            	.replace(android.R.id.content, currentFragment)
                .commit();
        	return true;
        }
        return super.onOptionsItemSelected(item);
    }
    
    @Override
    public void onBackPressed(){
    	if(currentFragment != null){
    		getFragmentManager().beginTransaction()
    		.detach(currentFragment)
    		.commit();
    		currentFragment = null;
    	}else{
    		super.onBackPressed();
    	}
    }
    
    public void selectRingtone(View v){
    	RingtoneManager ringtoneManager = new RingtoneManager(this);
    	ringtoneManager.setType(RingtoneManager.TYPE_ALARM);
        Cursor alarmCursor = ringtoneManager.getCursor();
        CharSequence items[] = new CharSequence[alarmCursor.getCount()];
        for(int i = 0; i < alarmCursor.getCount(); i++)
        	items[i] = ringtoneManager.getRingtone(i).getTitle(this.getApplicationContext());
    }

    @Override
    protected void onNewIntent(Intent intent){
        System.out.println("New intent");
    }
}
